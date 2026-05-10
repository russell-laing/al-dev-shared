# TDD Workflow - Shared Standards

**Version:** 2.19.0

This document defines the Test-Driven Development (TDD) workflow used across the AL development profile. It is referenced by agents and commands to ensure consistent TDD discipline.

---

## Core TDD Principles

### The TDD Cycle

```
RED → GREEN → REFACTOR → (repeat)
```

1. **RED:** Write a failing test
2. **GREEN:** Make it pass with minimal code
3. **REFACTOR:** Improve code quality without changing behavior

### Critical Rules

⛔ **NEVER** implement logic before user confirms test FAILS (RED phase)
⛔ **NEVER** skip approval gates between phases
⛔ **NEVER** batch multiple cycles - one test at a time
⛔ **ALWAYS** use AskUserQuestion at phase gates (BLOCKING)

---

## Phase 1: RED - Write Failing Test

### Goal
Create a test that fails because the production code doesn't exist yet.

### Steps

1. **Read test specification** from `.dev/05-test-specification.md`
2. **Implement test codeunit** following the spec:
   ```al
   codeunit 50200 "Credit Limit Tests"
   {
       Subtype = Test;

       [Test]
       procedure Test_ValidateCreditLimit_WithinLimit()
       var
           Validator: Codeunit "Credit Limit Validator";
           MockRepo: Codeunit "Mock Customer Repository";
           Result: Boolean;
       begin
           // [GIVEN] Customer with 10000 limit, 5000 outstanding
           MockRepo.AddMockCustomer('C001', 10000, 5000);

           // [WHEN] Validating order of 3000
           Result := Validator.ValidateCreditLimit('C001', 3000, MockRepo);

           // [THEN] Should allow (5000 + 3000 < 10000)
           Assert.IsTrue(Result, 'Should allow order within limit');
       end;
   }
   ```

3. **Implement mock repositories** for dependency injection
4. **Create MINIMAL production code stubs** (compilation only - NO logic):
   ```al
   codeunit 50100 "Credit Limit Validator"
   {
       procedure ValidateCreditLimit(
           CustomerNo: Code[20];
           OrderAmount: Decimal;
           Repo: Interface ICustomerRepository
       ): Boolean
       begin
           // ⛔ NO LOGIC! Just return default so test compiles and FAILS
           exit(false);  // or exit(true) - whichever makes test FAIL
       end;
   }
   ```

5. **Compile and publish app:**
   ```bash
   # Compile the app
   al-compile

   # Publish to BC server
   bc-publish
   ```

6. **Run the test:**
   ```bash
   # Execute the test codeunit
   # Auto-detects codeunit range from app.json if available
   bc-test -o .dev/test-results-red.txt

   # Or specify codeunit ID explicitly
   bc-test 50200 -o .dev/test-results-red.txt

   # Note: Results are written to file for clean conversation
   # Console shows summary only (e.g., "Passed: 0, Failed: 1")
   ```

7. **⛔ HARD STOP - Use AskUserQuestion:**
   ```markdown
   RED Phase Complete: [TestName]

   Test Results: Written to .dev/test-results-red.txt
   [Show summary from bc-test stdout - passed/failed counts]

   Did the test FAIL as expected?

   Options:
   - Yes - Test FAILED → Continue to GREEN phase
   - No - Test PASSED → ⚠️ TDD VIOLATION! Test is wrong or code exists
   - Compilation/deployment issue → Need troubleshooting
   ```

8. **Wait for user response** - DO NOT proceed to GREEN until user confirms FAIL

### RED Phase Violations

**If test PASSES in RED phase:**
```
❌ TDD VIOLATION: Test passed before production code exists!

This means:
- Test assertions are vacuous (testing nothing)
- Production code already exists somewhere
- Test specification is incorrect

⛔ CANNOT proceed to GREEN phase.
⛔ DO NOT write any production code.

Please investigate the test.
```

**STOP HERE. Wait for user.**

---

## Phase 2: GREEN - Make It Pass

### Goal
Write minimal production code to make the test pass.

### Steps

1. **NOW implement ACTUAL production logic** (replace RED phase stubs):
   ```al
   codeunit 50100 "Credit Limit Validator"
   {
       procedure ValidateCreditLimit(
           CustomerNo: Code[20];
           OrderAmount: Decimal;
           Repo: Interface ICustomerRepository
       ): Boolean
       var
           Customer: Record Customer;
           Outstanding: Decimal;
       begin
           // ✅ ACTUAL LOGIC (minimal to make test pass)
           if not Repo.TryGetCustomer(CustomerNo, Customer) then
               Error('Customer not found');

           if Customer.CreditLimit = 0 then
               exit(true); // Unlimited

           Outstanding := Repo.GetOutstandingAmount(CustomerNo);
           exit(Outstanding + OrderAmount <= Customer.CreditLimit);
       end;
   }
   ```

2. **Implement real interface implementations** (repositories, services)
3. **Compile and publish app:**
   ```bash
   # Compile the app
   al-compile

   # Publish to BC server
   bc-publish
   ```

4. **Run the test:**
   ```bash
   # Execute the test codeunit
   # Auto-detects codeunit range from app.json if available
   bc-test -o .dev/test-results-green.txt

   # Or specify codeunit ID explicitly
   bc-test 50200 -o .dev/test-results-green.txt

   # Note: Results are written to file for clean conversation
   # Console shows summary only (e.g., "Passed: 1, Failed: 0")
   ```

5. **⛔ HARD STOP - Use AskUserQuestion:**
   ```markdown
   GREEN Phase Complete: [TestName]

   Test Results: Written to .dev/test-results-green.txt
   [Show summary from bc-test stdout - passed/failed counts]

   Did the test PASS?

   Options:
   - Yes - Test PASSED → Continue to REFACTOR
   - No - Test still FAILS → Fix implementation
   - Compilation/deployment issue → Need troubleshooting
   ```

6. **Wait for user response** - DO NOT proceed to REFACTOR until user confirms PASS

### GREEN Phase Iterations

**If test still FAILS:**
1. Ask user for error message
2. Analyze failure
3. Fix production code
4. Re-ask AskUserQuestion for GREEN phase
5. Repeat until test PASSES

**Do NOT move to REFACTOR until test PASSES.**

---

## Phase 3: REFACTOR - Improve Quality

### Goal
Improve code quality without changing behavior.

### What to Refactor

✅ **Do refactor:**
- Extract helper procedures
- Improve variable names
- Add XML documentation
- Separate pure from impure functions
- Optimize performance
- Remove duplication

❌ **Don't refactor:**
- Behavior changes (creates new test failures)
- Add new features (requires new tests first)
- Change interfaces (breaks other tests)

### Steps

1. **Improve code quality:**
   ```al
   /// <summary>
   /// Validates that a new order does not exceed customer credit limit.
   /// </summary>
   procedure ValidateCreditLimit(...): Boolean
   var
       Customer: Record Customer;
   begin
       Customer := GetCustomer(CustomerNo, Repo);

       if IsUnlimitedCredit(Customer) then
           exit(true);

       exit(IsWithinCreditLimit(Customer, OrderAmount, Repo));
   end;

   local procedure GetCustomer(...): Record Customer
   local procedure IsUnlimitedCredit(...): Boolean
   local procedure IsWithinCreditLimit(...): Boolean
   ```

2. **Compile and publish app:**
   ```bash
   # Compile the app
   al-compile

   # Publish to BC server
   bc-publish
   ```

3. **Run ALL tests:**
   ```bash
   # Execute all test codeunits to verify refactoring didn't break anything
   # Auto-detects full codeunit range from app.json
   bc-test -o .dev/test-results-refactor.txt

   # Or specify multiple codeunits explicitly
   bc-test 50200 50201 -o .dev/test-results-refactor.txt

   # Or use ranges for consecutive codeunit IDs
   bc-test 50200-50210 -o .dev/test-results-refactor.txt

   # Note: Results written to file for detailed review
   # Console shows summary (e.g., "Passed: 10, Failed: 0")
   ```

4. **⛔ HARD STOP - Use AskUserQuestion:**
   ```markdown
   REFACTOR Phase Complete

   Test Results: Written to .dev/test-results-refactor.txt
   [Show summary from bc-test stdout - passed/failed counts]

   All tests still PASS after refactoring. Please review results.

   Options:
   - Approve → Continue to next test
   - Some tests FAILED → Revert refactoring
   - Need troubleshooting → Investigate failures
   ```

5. **Wait for user response** - DO NOT continue until user confirms all tests PASS

### REFACTOR Phase Failures

**If refactoring broke tests:**
1. **Revert** refactoring immediately
2. Document: "Refactoring reverted - broke tests"
3. Skip further refactoring for this test
4. Continue to next test (refactoring is optional)

---

## TDD Log Documentation

**Every cycle MUST be documented in `.dev/03-tdd-log.md`:**

```markdown
## Feature: Credit Limit Validation

### Cycle 1: Basic Within-Limit Validation

#### RED Phase ✓
- Test: `Test_ValidateCreditLimit_WithinLimit`
- Status: ❌ FAILS as expected
- Error: "Method ValidateCreditLimit not found"
- Reason: Production code stub returns wrong value

#### GREEN Phase ✓
- Production code: Implemented Credit Limit Validator
- Interfaces: ICustomerRepository defined
- Test status: ✅ PASSES

#### REFACTOR Phase ✓
- Extracted helper procedures
- Added XML documentation
- All tests: ✅ PASS (1/1 tests)

**Cycle 1 Complete** ✓
```

---

## Task Management for TDD Cycles

**Agents should create granular tasks for each TDD cycle:**

```
TaskCreate: "TDD RED: [test name]"
  description: "Write failing test for [brief description]"
  activeForm: "Writing failing test: [test name]"

TaskCreate: "TDD GREEN: [test name]"
  description: "Implement production code to make test pass"
  activeForm: "Implementing: [production procedure name]"

TaskCreate: "TDD REFACTOR: [test name]"
  description: "Refactor code for quality"
  activeForm: "Refactoring: [test name]"

# Set dependencies
TaskUpdate: "TDD GREEN: [test]" → addBlockedBy: ["TDD RED: [test]"]
TaskUpdate: "TDD REFACTOR: [test]" → addBlockedBy: ["TDD GREEN: [test]"]
```

**Update task status at each gate:**
- After RED confirmation → mark RED complete, start GREEN
- After GREEN confirmation → mark GREEN complete, start REFACTOR
- After REFACTOR confirmation → mark REFACTOR complete, start next test

---

## Test Execution Context

**AL tests can be executed automatically using bc-publish and bc-test:**
- Agents use `bc-publish` to deploy .app files to BC server
- Agents use `bc-test [codeunit-id]` to execute test codeunits
- Requires `.bcconfig.json` with server configuration
- Each TDD cycle includes automated test execution with approval gates
- Agent presents test results to user for verification

**This ensures TDD discipline is followed** - test results are verified at each gate.

---

## Advanced bc-test Features

### Auto-Detection from app.json

**bc-test can automatically detect the test codeunit range:**

```bash
# No codeunit IDs needed - auto-detects from app.json
bc-test

# Reads first idRange from app.json in current directory
# Example: {"from": 83200, "to": 83299} → runs 83200-83299
```

**Benefits:**
- No need to remember codeunit IDs
- Works across projects automatically
- Updates when app.json changes

### File Output Options

**Write detailed results to file instead of flooding console:**

```bash
# Text format (human-readable with full call stacks)
bc-test -o .dev/test-results.txt

# JSON format (machine-readable for CI/CD)
bc-test -o .dev/test-results.json -f json

# Console shows summary only:
# "Passed: 558, Failed: 9"
```

**JSON Structure:**
```json
{
  "total_tests_run": 567,
  "passed": 558,
  "failed": 9,
  "showing": "all",
  "tests": [
    {
      "codeunitId": 83220,
      "codeunitName": "Credit Limit Tests",
      "functionName": "Test_ValidateCreditLimit_WithinLimit",
      "success": true,
      "errorMessage": "",
      "callStack": ""
    }
  ]
}
```

### Failures-Only Filter

**Focus on what needs attention:**

```bash
# Show only failed tests (console output)
bc-test --failures-only

# Save only failures to file
bc-test -o .dev/failures.txt --failures-only

# Example: 567 tests → 9 failures shown
# Header: "9 failures (out of 567 total)"
```

**Use cases:**
- Quick identification of problems
- Reduced noise in large test suites
- CI/CD failure reports

### Smart Defaults

**bc-test adapts to your workflow:**

**Console output (no `-o`):**
- Defaults to `--failures-only` (less noise)
- Shows summary statistics always
- Override: `bc-test --no-failures-only` to see all

**File output (with `-o`):**
- Defaults to show all tests (complete record)
- Includes full details and call stacks
- Override: `bc-test -o file.txt --failures-only` for failures only

### CI/CD Integration

**Use JSON format for automated pipelines:**

```bash
# Export test results for CI/CD
bc-test -o test-results.json -f json

# Parse with jq for failed tests
jq '.tests[] | select(.success == false)' test-results.json

# Check if any tests failed
if jq -e '.failed > 0' test-results.json; then
  echo "Tests failed!"
  exit 1
fi
```

### Example Workflows

**Quick check during development:**
```bash
# See only what's broken
bc-test
# Output: "9 failures (out of 567 total)" + failure details
```

**Comprehensive documentation:**
```bash
# Save complete test run for records
bc-test -o .dev/test-run-$(date +%Y%m%d).txt
# File contains all tests with full details
```

**Automated testing:**
```bash
# CI/CD pipeline
bc-test -o results.json -f json --failures-only
# Upload results.json as artifact
```

---

## BC Configuration Requirements

**Agents require `.bcconfig.json` to run tests:**

```json
{
  "server": "http://localhost",
  "port": 7048,
  "instance": "BC",
  "tenant": "default",
  "username": "admin",
  "password": "Admin123!",
  "apiInstance": "BC",
  "apiPassword": "your-web-service-key",
  "schemaUpdateMode": "synchronize"
}
```

- Create `.bcconfig.json` in project root or home directory
- Use `bc-publish --init` to create template
- `apiPassword` should be web service access key (for bc-test OData access)
- `password` is for dev endpoint publishing

## Summary: The Hard Stops

```
1. Write test code + minimal stubs
2. Compile, publish, run test (agent verifies FAIL)
3. ⛔ STOP → Agent shows results, user reviews and confirms
4. Write production code
5. Compile, publish, run test (agent verifies PASS)
6. ⛔ STOP → Agent shows results, user reviews and confirms
7. Refactor code
8. Compile, publish, run ALL tests (agent verifies all PASS)
9. ⛔ STOP → Agent shows results, user reviews and confirms
10. Move to next test →
```

**Three hard stops per test. No exceptions.**

---

**Remember:** TDD's value comes from seeing tests fail BEFORE implementing logic. Skipping RED phase verification destroys this value.
