import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, '/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/plugin-health')

from schemas import CheckpointState

def read_lens_result(result_path: str) -> dict | None:
    """Read a single lens result artifact."""
    path = Path(result_path)
    if not path.exists():
        return None

    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to read {result_path}: {e}")
        return None

def aggregate_findings(run_dir: str, manifest_path: str) -> dict:
    """Aggregate all lens results from the run directory.

    Returns: dict mapping lens_name -> findings_block
    """
    findings = {}

    # Read manifest to see which lenses completed
    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        print(f"Warning: Manifest not found at {manifest_path}")
        return findings

    with open(manifest_file, "r") as f:
        manifest = json.load(f)

    # Read each completed lens result
    results_dir = Path(run_dir) / "lens-results"
    for entry in manifest.get("completed", []):
        lens_name = entry.get("name", "")
        result_file = results_dir / f"{lens_name}.json"

        result = read_lens_result(str(result_file))
        if result:
            findings[lens_name] = result.get("findings_block", "")

    return findings

def write_findings_file(surface: str, findings: dict, failed_lenses: list) -> str:
    """Write aggregated findings to docs/health/YYYY-MM-DD-<surface>-findings.md"""
    repo_root = Path("/Users/russelllaing/al-dev-shared")
    findings_dir = repo_root / "docs" / "health"
    findings_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    findings_file = findings_dir / f"{date_str}-{surface}-findings.md"

    # Build markdown content
    content = f"# {surface.capitalize()} Findings — {date_str}\n\n"
    content += "## Raw Lens Output\n\n"

    for lens_name, findings_block in findings.items():
        # Format lens name for display
        display_name = lens_name.replace("-", " ").title()
        content += f"### {display_name}\n\n"
        content += findings_block
        content += "\n\n---\n\n"

    # Add failed lenses section
    if failed_lenses:
        content += "## Failed Lenses\n\n"
        for failed in failed_lenses:
            content += f"- {failed['name']} ({failed['error']})\n"
        content += "\n"

    # Write file
    try:
        with open(findings_file, "w") as f:
            f.write(content)
        return str(findings_file)
    except Exception as e:
        print(f"Error: Failed to write findings file: {e}")
        raise

def write_dossier(surface: str, findings_file: str, completed_count: int, total_count: int) -> str:
    """Write health dossier to docs/health/YYYY-MM-DD-<surface>-health.md

    This would normally contain ranked suggestions (top 5), but for now
    write a summary linking to findings.
    """
    repo_root = Path("/Users/russelllaing/al-dev-shared")
    health_dir = repo_root / "docs" / "health"
    health_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    dossier_file = health_dir / f"{date_str}-{surface}-health.md"

    status_str = "COMPLETE" if completed_count == total_count else f"PARTIAL ({completed_count}/{total_count})"

    content = f"# {surface.capitalize()} Health Report — {date_str}\n\n"
    content += f"**Status:** {status_str}\n\n"
    content += f"## Summary\n\n"
    content += f"Lenses executed: {completed_count}/{total_count}\n\n"
    content += f"**Detailed findings:** See {Path(findings_file).name}\n\n"

    if completed_count < total_count:
        content += f"**Note:** {total_count - completed_count} lenses remain pending. "
        content += "Run `/plugin-health --resume` to complete the sweep.\n"

    content += "\n## Next Steps\n\n"
    content += "Use `/superpowers:writing-plans` to implement top recommendations from findings.\n"

    try:
        with open(dossier_file, "w") as f:
            f.write(content)
        return str(dossier_file)
    except Exception as e:
        print(f"Error: Failed to write dossier: {e}")
        raise

def collect_results(checkpoint: CheckpointState) -> bool:
    """Main collection orchestration.

    Returns: True if collection succeeded, False otherwise
    """
    run_dir = checkpoint.result_dir
    manifest_path = checkpoint.manifest_path

    # Read manifest to check status
    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        return False

    with open(manifest_file, "r") as f:
        manifest = json.load(f)

    completed = manifest.get("completed", [])
    pending = manifest.get("pending", [])
    failed = manifest.get("failed", [])
    total = manifest.get("total_lenses", 0)

    print(f"Results: {len(completed)}/{total} lenses completed")

    # Aggregate findings
    findings = aggregate_findings(run_dir, manifest_path)

    # Write findings file
    findings_file = write_findings_file(checkpoint.surface, findings, failed)
    print(f"Findings written to {findings_file}")

    # Write dossier
    dossier_file = write_dossier(checkpoint.surface, findings_file, len(completed), total)
    print(f"Dossier written to {dossier_file}")

    # Update checkpoint
    checkpoint.findings_file = findings_file
    checkpoint.dossier_file = dossier_file
    checkpoint.collected_at = datetime.now().isoformat()
    checkpoint.status = "collected" if len(pending) == 0 else "partial"

    # Save updated checkpoint
    checkpoint_path = Path("/Users/russelllaing/al-dev-shared/.dev/plugin-health-team-checkpoint.json")
    try:
        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint.to_dict(), f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to update checkpoint: {e}")

    return True
