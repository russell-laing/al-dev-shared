# Quality Checklist

Use these checklists when reviewing agent deliverables at each phase gate. Every item should be verified before approving and passing work to the next phase.

**For solution plans:**
- [ ] All requirements from the latest `.dev/*-al-dev-interview-requirements.md` are addressed
- [ ] Data model is complete (all entities, fields, relationships, constraints)
- [ ] Error handling strategy is defined, not hand-waved
- [ ] Integration points are explicit (events, APIs, dependencies)
- [ ] Testability strategy is included
- [ ] AL object numbering and naming follow conventions

**For code implementation:**
- [ ] All components from the solution plan are implemented
- [ ] Error handling is present and meaningful (clear failure paths, user-facing messages, and no empty suppression logic)
- [ ] Input validation exists at public boundaries
- [ ] SetLoadFields is used where only a small subset of fields is read and loading full rows would be wasteful
- [ ] Field naming follows `Prefix + Descriptive Name` convention
- [ ] Events are published where extensibility is expected
- [ ] No hardcoded magic numbers or strings

**For test suites:**
- [ ] Happy path is covered for every user story
- [ ] Edge cases include: empty data, boundary values, invalid input, concurrent access
- [ ] Error paths are tested (what happens when things fail?)
- [ ] Integration tests verify cross-object workflows
- [ ] Test names clearly describe what they verify
