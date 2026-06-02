# Workflow Lens Dispatch Reference

The plugin health discovery phase uses JavaScript Workflow to fan out lens agents in parallel.

## Building the Lens Prompt List

Each lens needs minimal context. Construct a prompt object per lens. Use
`agentType` consistently; the Workflow script reads `lens.agentType`.

```python
lens_prompt_list = []

for lens_name in remaining_lenses:
    lens_prompt = {
        "name": lens_name,
        "agentType": lens_name,  # e.g. "design-agent-lens-tool-hygiene"
        "prompt": f"""
Run the {lens_name} analysis.

Files to analyze:
{formatted_file_list}

Context fields:
{context_field_content}
"""
    }
    lens_prompt_list.append(lens_prompt)
```

Context fields are defined per lens in `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`.

## Invoking the Workflow

The actual Workflow script (`workflow-lens-dispatch.js` in the skill directory) is authoritative. It accepts a list of lens prompts and runs them in parallel. This abbreviated excerpt shows the contract the skill relies on:

```javascript
export const meta = {
  name: 'plugin-health-lens-sweep',
  description: 'Fan out plugin health lens agents in parallel, return structured findings',
  phases: [{ title: 'Lens sweep' }]
}

const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['lens', 'findings', 'suggestion_count'],
  properties: {
    lens:             { type: 'string' },
    findings:         { type: 'string' },
    suggestion_count: { type: 'number' }
  }
}

// args = [{ name, agentType, prompt }]
const results = await pipeline(
  args,
  lens => agent(
    lens.prompt,
    {
      label:      lens.name,
      phase:      'Lens sweep',
      schema:     FINDINGS_SCHEMA,
      agentType:  lens.agentType
    }
  )
)

return results.filter(Boolean)
```

## Handling Results

Each successful lens returns a structured JSON object (~1KB) containing the lens name, findings block, and suggestion count. The Workflow returns `results.filter(Boolean)`, so only truthy lens result objects are passed back to the skill. These are collected and written to `.dev/` as individual files for assembly in Phase 4.

The current Workflow script does not emit a `failed_lenses` list. If a requested lens is missing from the returned results, detect that by comparing returned lens identifiers with the requested prompt list and note the missing lens in the findings output.
