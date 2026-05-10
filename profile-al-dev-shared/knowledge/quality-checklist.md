# Quality Checklist

Use these checklists when reviewing agent deliverables at each phase gate. Every item should be verified before approving and passing work to the next phase.

### Quality Checklist

**For solution plans:**
- [ ] All requirements from `.dev/01-requirements.md` are addressed
- [ ] Data model is complete (all entities, fields, relationships, constraints)
- [ ] Error handling strategy is defined, not hand-waved
- [ ] Integration points are explicit (events, APIs, dependencies)
- [ ] Testability strategy is included
- [ ] AL object numbering and naming follow conventions

**For code implementation:**
- [ ] All components from the solution plan are implemented
- [ ] Error handling is present and meaningful (not empty catch blocks)
- [ ] Input validation exists at public boundaries
- [ ] SetLoadFields is used for record variables accessed across tables
- [ ] Field naming follows `Prefix + Descriptive Name` convention
- [ ] Events are published where extensibility is expected
- [ ] No hardcoded magic numbers or strings

**For test suites:**
- [ ] Happy path is covered for every user story
- [ ] Edge cases include: empty data, boundary values, invalid input, concurrent access
- [ ] Error paths are tested (what happens when things fail?)
- [ ] Integration tests verify cross-object workflows
- [ ] Test names clearly describe what they verify
