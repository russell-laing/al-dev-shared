#!/usr/bin/env python3
"""Extract Mermaid blocks from Markdown and render reviewable image artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


FENCE_START = re.compile(
    r"^(?P<indent>\s*)(?P<fence>`{3,}|~{3,})\s*mermaid(?:\s+.*)?$",
    re.IGNORECASE,
)
COLON_START = re.compile(r"^\s*:::\s*mermaid(?:\s+.*)?$", re.IGNORECASE)
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass
class Diagram:
    source_file: Path
    index: int
    start_line: int
    end_line: int
    source: str
    heading: str | None
    diagram_id: str
    source_path: Path | None = None
    images: dict[str, Path] = field(default_factory=dict)
    render_errors: dict[str, str] = field(default_factory=dict)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract Mermaid code blocks from Markdown and render them with mmdc.",
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="Markdown files to scan")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("mermaid-diagrams"),
        help="Output directory for images, sources, manifest, and index",
    )
    parser.add_argument(
        "--format",
        action="append",
        choices=("png", "svg", "pdf"),
        dest="formats",
        help="Output format. Repeat for multiple formats. Defaults to png.",
    )
    parser.add_argument("--mmdc", default="mmdc", help="Mermaid CLI executable")
    parser.add_argument("--theme", default="default", help="Mermaid theme for mmdc")
    parser.add_argument(
        "--background",
        default="white",
        help="Background color for PNG/SVG output",
    )
    parser.add_argument("--width", type=int, default=1600, help="Render viewport width")
    parser.add_argument("--height", type=int, default=1200, help="Render viewport height")
    parser.add_argument("--scale", default="1", help="Puppeteer scale factor")
    parser.add_argument("--config-file", type=Path, help="Mermaid JSON config file")
    parser.add_argument("--css-file", type=Path, help="CSS file for rendered diagrams")
    parser.add_argument(
        "--puppeteer-config",
        type=Path,
        help="Puppeteer JSON config file for mmdc",
    )
    parser.add_argument(
        "--no-render",
        action="store_true",
        help="Only extract .mmd sources and metadata; do not run mmdc",
    )
    return parser.parse_args()


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or fallback


def path_slug(path: Path) -> str:
    try:
        raw = str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        raw = str(path.resolve())
    stem = slugify(raw, path.stem)
    digest = hashlib.sha1(str(path.resolve()).encode("utf-8")).hexdigest()[:8]
    return f"{stem}-{digest}"


def nearest_heading(lines: list[str], line_index: int) -> str | None:
    for prior in range(line_index - 1, -1, -1):
        match = HEADING.match(lines[prior])
        if match:
            return match.group(2).strip()
    return None


def find_fence_end(lines: list[str], start_index: int, fence: str) -> int | None:
    char = re.escape(fence[0])
    min_len = len(fence)
    closing = re.compile(rf"^\s*{char}{{{min_len},}}\s*$")
    for line_index in range(start_index + 1, len(lines)):
        if closing.match(lines[line_index]):
            return line_index
    return None


def find_colon_end(lines: list[str], start_index: int) -> int | None:
    closing = re.compile(r"^\s*:::\s*$")
    for line_index in range(start_index + 1, len(lines)):
        if closing.match(lines[line_index]):
            return line_index
    return None


def extract_diagrams(path: Path) -> list[Diagram]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    diagrams: list[Diagram] = []
    line_index = 0

    while line_index < len(lines):
        line = lines[line_index]
        fence_match = FENCE_START.match(line)
        colon_match = COLON_START.match(line)

        if fence_match:
            end_index = find_fence_end(lines, line_index, fence_match.group("fence"))
        elif colon_match:
            end_index = find_colon_end(lines, line_index)
        else:
            line_index += 1
            continue

        if end_index is None:
            raise ValueError(f"Unclosed Mermaid block in {path} at line {line_index + 1}")

        source_lines = lines[line_index + 1 : end_index]
        source = "\n".join(source_lines).strip("\n")
        index = len(diagrams) + 1
        heading = nearest_heading(lines, line_index)
        diagram_id = f"{path_slug(path)}-diagram-{index:02d}"
        diagrams.append(
            Diagram(
                source_file=path,
                index=index,
                start_line=line_index + 1,
                end_line=end_index + 1,
                source=source,
                heading=heading,
                diagram_id=diagram_id,
            )
        )
        line_index = end_index + 1

    return diagrams


def normalize_inputs(inputs: Iterable[Path]) -> list[Path]:
    normalized = []
    for path in inputs:
        resolved = path.expanduser().resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"Input does not exist: {path}")
        if resolved.is_dir():
            normalized.extend(sorted(resolved.rglob("*.md")))
        else:
            normalized.append(resolved)
    return normalized


def write_sources(diagrams: list[Diagram], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for diagram in diagrams:
        path = output_dir / f"{diagram.diagram_id}.mmd"
        path.write_text(diagram.source + "\n", encoding="utf-8")
        diagram.source_path = path


def mmdc_command(args: argparse.Namespace, source_path: Path, image_path: Path, fmt: str) -> list[str]:
    command = [
        args.mmdc,
        "-i",
        str(source_path),
        "-o",
        str(image_path),
        "-e",
        fmt,
        "-t",
        args.theme,
        "-w",
        str(args.width),
        "-H",
        str(args.height),
        "-s",
        str(args.scale),
        "-q",
    ]
    if fmt != "pdf":
        command.extend(["-b", args.background])
    if args.config_file:
        command.extend(["-c", str(args.config_file)])
    if args.css_file:
        command.extend(["-C", str(args.css_file)])
    if args.puppeteer_config:
        command.extend(["-p", str(args.puppeteer_config)])
    return command


def render_diagrams(diagrams: list[Diagram], args: argparse.Namespace, output_dir: Path) -> None:
    if args.no_render:
        return

    executable = shutil.which(args.mmdc)
    if executable is None:
        raise RuntimeError(f"Mermaid CLI not found in PATH: {args.mmdc}")

    formats = args.formats or ["png"]
    for diagram in diagrams:
        if diagram.source_path is None:
            raise RuntimeError(f"Source path missing for {diagram.diagram_id}")
        for fmt in formats:
            image_path = output_dir / f"{diagram.diagram_id}.{fmt}"
            command = mmdc_command(args, diagram.source_path, image_path, fmt)
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and image_path.exists():
                diagram.images[fmt] = image_path
            else:
                error = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
                diagram.render_errors[fmt] = error or f"mmdc exited with {result.returncode}"


def relative(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path)


def write_manifest(diagrams: list[Diagram], args: argparse.Namespace, output_dir: Path) -> Path:
    manifest = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "inputs": [str(path) for path in map(Path.resolve, args.inputs)],
        "formats": args.formats or ["png"],
        "rendered": not args.no_render,
        "diagrams": [],
    }

    for diagram in diagrams:
        manifest["diagrams"].append(
            {
                "id": diagram.diagram_id,
                "source_file": str(diagram.source_file),
                "start_line": diagram.start_line,
                "end_line": diagram.end_line,
                "heading": diagram.heading,
                "source_path": relative(diagram.source_path, output_dir)
                if diagram.source_path
                else None,
                "images": {fmt: relative(path, output_dir) for fmt, path in diagram.images.items()},
                "render_errors": diagram.render_errors,
            }
        )

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def write_index(diagrams: list[Diagram], output_dir: Path) -> Path:
    lines = ["# Mermaid Diagram Index", ""]
    for diagram in diagrams:
        title = diagram.heading or f"Diagram {diagram.index}"
        lines.extend(
            [
                f"## {diagram.diagram_id}",
                "",
                f"- Source: `{diagram.source_file}:{diagram.start_line}`",
                f"- Heading: {title}",
            ]
        )
        if diagram.images:
            for fmt, path in sorted(diagram.images.items()):
                rel = relative(path, output_dir)
                if fmt in {"png", "svg"}:
                    lines.extend(["", f"![{diagram.diagram_id} {fmt}]({rel})"])
                else:
                    lines.extend(["", f"- {fmt.upper()}: [{rel}]({rel})"])
        if diagram.render_errors:
            lines.append("")
            lines.append("Render errors:")
            for fmt, error in sorted(diagram.render_errors.items()):
                compact = error.replace("\n", " ").strip()
                if len(compact) > 500:
                    compact = compact[:497] + "..."
                lines.append(f"- {fmt}: {compact}")
        lines.extend(["", "```mermaid", diagram.source, "```", ""])

    index_path = output_dir / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def main() -> int:
    args = parse_args()
    try:
        input_files = normalize_inputs(args.inputs)
        args.inputs = input_files
        diagrams = []
        for path in input_files:
            diagrams.extend(extract_diagrams(path))
        if not diagrams:
            print("No Mermaid diagrams found.", file=sys.stderr)
            return 1

        output_dir = args.out.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        write_sources(diagrams, output_dir)
        render_diagrams(diagrams, args, output_dir)
        manifest_path = write_manifest(diagrams, args, output_dir)
        index_path = write_index(diagrams, output_dir)

        rendered_count = sum(len(diagram.images) for diagram in diagrams)
        error_count = sum(len(diagram.render_errors) for diagram in diagrams)
        print(f"Extracted {len(diagrams)} Mermaid diagram(s).")
        print(f"Rendered {rendered_count} image artifact(s).")
        print(f"Manifest: {manifest_path}")
        print(f"Index: {index_path}")
        return 2 if error_count else 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
