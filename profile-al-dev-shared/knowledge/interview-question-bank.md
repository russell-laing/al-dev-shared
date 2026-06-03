# Interview Question Bank for BC/AL Projects

Used by: `al-dev-interview` agent

## Question Categories

Use these categories to structure BC/AL project interviews. Adapt questions to the specific project context.

### Business Requirements

- What is the primary business problem this module solves?
- Who are the end users and what is their workflow?
- What are the success criteria — how will we measure success (e.g., time saved, error reduction, throughput, adoption)?
- What are the constraints (timeline, budget, regulatory)?
- Are there any manual processes today that this module will automate?

### Data Model

- What tables and fields are affected?
- Are there relationships to standard BC tables (e.g., Customer, Vendor, Item)?
- What data transformations are needed?
- How much data will be stored (ballpark)?
- Are there archival or data retention requirements?

### Integration Points

- Does this module integrate with external systems?
- What APIs or webhooks are required?
- What are the integration failure modes and recovery steps?
- What's the expected latency for integrations (synchronous response time, batch completion time, or both)?
- Are there batch processing requirements?

### Performance & Scaling

- What is the expected data volume (now and in 2 years)?
- What are the performance SLAs (response time, throughput)?
- What's the expected user concurrency?
- Are there peak usage patterns (month-end, year-end)?

### Security & Compliance

- What data is sensitive (PII, financial, regulatory)?
- What are the access control requirements?
- Are there compliance rules to follow (GDPR, SOX, industry-specific)?
- How should audit trails be maintained?
- What encryption or data masking is needed?

### Testing & UAT

- What test scenarios are critical?
- Who performs UAT and when?
- What is the rollback plan?
- How will data be validated after deployment?
- Are there any regulatory testing requirements?

### Maintenance & Support

- Who maintains this after launch?
- What monitoring and alerting is needed?
- What's the escalation process for production issues?
- How will the team learn the system?
- Are there known limitations or future enhancements?

## Interview Guidelines

### Clarification Technique
When an answer is vague, ask for specifics:
- Bad: "We need better reporting"
- Good: "What metrics do you need to see? How often? Who's the audience?"

### Handling Ambiguity
When requirements conflict, don't decide — document the conflict and note that it needs to be resolved:
- "I see a tension between [A] and [B]. Let's document that and escalate to stakeholders."

### Follow-Up Questions
For each answer, ask "Why is that important?" and "What would failure look like?"

## Tips for Effective Interviews

1. **Listen more than you talk** — ask open-ended questions
2. **Don't assume jargon** — clarify terms (e.g., "report" could mean PDF, interactive dashboard, email)
3. **Document assumptions** — "So if I understand correctly, [assumption]. Is that right?"
4. **Prioritize ruthlessly** — ask "nice-to-have vs. must-have"
5. **Confirm understanding** — repeat back what you heard to verify
