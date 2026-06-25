# Adaptive: Building Self-Healing AI Agents - Summary

Source: https://medium.com/@madhur.prashant7/evolve-building-self-healing-ai-agents-a-multi-agent-system-for-continuous-optimization-0d711ead090c

## Main idea

The article proposes a self-healing agent system that continuously improves itself from production observability data. Instead of manually reviewing traces and editing prompts, the system uses specialized agents to analyze performance, generate optimization proposals, and route changes through human approval.

## Problem being solved

- Static prompts do not keep up with dynamic production environments.
- Observability data from tools like LangSmith and Langfuse is useful, but the analysis loop is mostly manual.
- Manual trace review is slow, biased toward obvious failures, and hard to scale across multiple agents and domains.

## The proposed system

The architecture uses three cooperating agent roles:

1. Insights Agent
   - Pulls execution traces from observability platforms.
   - Analyzes errors, tool usage, reasoning patterns, and workflow bottlenecks.
   - Uses persistent memory so it can build on previous findings across sessions.

2. Evolution Agent
   - Converts insights into concrete prompt or configuration changes.
   - Reads the existing repository or prompt files.
   - Produces specific optimization proposals and checks them for structure and side effects.

3. Routing Agent
   - Decides whether the user needs analysis only or should also get optimization proposals.
   - Orchestrates the workflow between insight gathering and evolution.

## Technical approach

- Built on Amazon Bedrock with Claude models.
- Uses LangGraph for the stateful multi-agent workflow.
- Integrates observability systems through the Model Context Protocol.
- Uses Bedrock AgentCore Memory for long-term conversational and analytical context.
- Applies middleware for token limits, summarization, pruning, and tool-response compression.

## Safety and control

- Prompt changes are never applied automatically.
- Proposed edits are shown as unified diffs.
- Users can inspect stats and optionally review changes in VS Code.
- Human approval is required before any production prompt update is committed.
- File access is restricted and validated to prevent unsafe repository writes.

## Context engineering

The article emphasizes keeping context bounded and useful over long sessions. It does this by:

- Retrieving only semantically relevant historical memory.
- Summarizing older conversation history.
- Compressing large tool outputs.
- Pruning verbose tool-call artifacts.

This keeps the agent effective over long-running optimization workflows without overflowing context windows.

## Practical takeaway

The core pattern is a feedback loop: observe production behavior, turn traces into insights, convert insights into safe optimization proposals, and keep a human in the loop for approval. The result is a multi-agent system that can improve itself continuously without losing control over changes.
