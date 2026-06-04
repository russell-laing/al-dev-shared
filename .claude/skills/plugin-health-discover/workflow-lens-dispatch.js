export const meta = {
  name: 'plugin-health-lens-sweep',
  description: 'Dispatch plugin health lens agents in parallel, return structured findings',
  phases: [{ title: 'Lens sweep' }]
}

const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['lens', 'findings', 'suggestion_count'],
  properties: {
    lens:             { type: 'string', description: 'Lens identifier' },
    findings:         { type: 'string', description: 'Lens findings block (markdown)' },
    suggestion_count: { type: 'number', description: 'Number of suggestions returned' }
  }
}

// Input: args = [
//   { name: 'design-agent-lens-tool-hygiene', agentType: 'design-agent-lens-tool-hygiene', prompt: '...' },
//   ...
// ]
// Some harnesses deliver args as a JSON-encoded string — parse defensively.
const lensList = typeof args === 'string' ? JSON.parse(args) : args

const results = await pipeline(
  lensList,
  async (lens) => {
    return await agent(
      lens.prompt,
      {
        label:      lens.name,
        phase:      'Lens sweep',
        schema:     FINDINGS_SCHEMA,
        agentType:  lens.agentType
      }
    )
  }
)

return results.filter(Boolean)
