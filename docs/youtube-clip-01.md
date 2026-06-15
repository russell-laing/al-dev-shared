# **Superpowers: Token Optimization for AI Agents**

**Last updated:** 2026-06-16

In the video, we explored seven powerful tools for optimizing token usage in AI agents. However, the true art of context management extends beyond these tools into a broader framework of strategies that can significantly enhance the efficiency and effectiveness of your AI agents.

## Summary of the Tools Covered in the Video

### **Expanded Token Optimization Framework**

Beyond the seven tools mentioned in the video, effective context management relies on a shift from "brute-forcing" information into the AI to a "just-in-time" retrieval model.

#### **1. Advanced Context Structuring & Compression**

- **Hierarchical Summarization:** Instead of keeping the entire conversation history, adopt a rolling context strategy. Periodically summarize completed subtasks or earlier exchanges into a "key findings" or "state" file, keeping only the most recent interactions in full detail.
- **Prompt Caching:** Many AI providers now offer prompt caching, which can reduce costs by up to 90% for repeated inputs. Ensure your system prompts and core documentation files (like `claude.md`) are consistently structured so they can be effectively cached.
- **Semantic Tool Selection:** If you manage many custom tools, avoid loading every definition into every request. Implement a selection layer—like a vector database (e.g., Redis)—that retrieves only the 2–3 tools relevant to the specific user intent.

#### **2. Refining the "Agent Experience" (`claude.md`)**

- **The "Goldilocks" Principle:** Your `claude.md` should be at the right altitude—neither so sparse that the agent lacks direction, nor so bloated with "laundry lists" of edge cases that it triggers context rot.
- **Verifiable Evidence:** Shift instructions from general goals ("write clean code") to verifiable criteria ("run `test_file.ts` and ensure it passes, then list any remaining failures").
- **Progressive Disclosure:** Use the `claude.md` file as an index. Instead of writing long tutorials, use the file to point the agent to specific documentation files (e.g., `@docs/architecture.md`) that it should only consult when specific tasks are requested.

#### **3. Architectural Efficiency**

- **Codebase Modularization:** Agents often struggle with massive, monolithic files. Splitting large modules into smaller, focused files allows the agent to read only the logic it needs rather than pulling in hundreds of lines of irrelevant code.
- **Naming for Searchability:** Use descriptive, domain-aligned naming conventions (e.g., `OrderProcessor` over `ServiceFactory`). Agents are far more efficient when they can navigate the file system using semantic names that accurately reflect their purpose.
- **Externalize Knowledge:** Move static knowledge (API docs, style guides) out of the LLM context and into external storage or documentation files that the agent can "look up" using tools, similar to how a human developer consults a manual.

#### **4. Measuring & Iterating (The "Gain" Mindset)**

- **Establish a Baseline:** Before optimizing, measure your average tokens-per-request.
- **A/B Testing Strategies:** If you implement a new tool (like a code graph or intent layer), compare performance metrics against your baseline. Do you reach the "correct" solution faster? Is the token usage lower?
- **Constraint Discipline:** Treat your token budget like a performance budget. If an agent is constantly hitting its limit, treat it as a technical debt item that needs refactoring—either by improving your documentation, narrowing the agent's scope, or optimizing your tool definitions.

### **Summary of Expert Recommendations**

| Strategy | Goal | Impact |
| --- | --- | --- |
| **Indexing** | Provide a "map" of the codebase via `claude.md` or `agent.md` files. | Reduces "discovery" tokens. |
| **Compaction** | Periodically summarize conversation history. | Prevents context window bloating. |
| **Tool Proxying** | Filter terminal output before it hits the AI (e.g., RTK). | Massive reduction in noisy input. |
| **RAG/Lookup** | Keep docs in external files, not the system prompt. | Lowers base token overhead. |

By treating your AI coding environment as a structured system rather than a black box, you can achieve significant cost savings—often reported up to **90%** in enterprise environments—without losing the agent's effectiveness or accuracy.
