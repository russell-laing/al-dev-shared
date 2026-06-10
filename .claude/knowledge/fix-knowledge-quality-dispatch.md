# fix-knowledge-quality Dispatch Template

Agent dispatch template for `/fix-knowledge-quality` Phase 3. Consumed when
`--auto-fix` mode is active. Substitute `{file}`, `{issue_type}`,
`{description}`, `{suggested_action}` from the parsed task before dispatching.

## Agent: al-dev-shared:al-dev-docs-writer

```text
Agent: al-dev-shared:al-dev-docs-writer
Prompt:
  Fix a knowledge file quality issue.

  File: {file}
  Issue type: {issue_type}
  Description: {description}
  Required action: {suggested_action}

  Read the file in full, apply the fix, and verify the result is coherent.
  Do not add content you are not confident about — mark genuine gaps with
  [NEEDS CONTENT: reason] instead of guessing.
  Return: a summary of what was changed and what (if any) was left for
  human review.
```
