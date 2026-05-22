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
⛔ **ALWAYS** use USER_GATE at phase gates (BLOCKING)

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

7. **⛔ HARD STOP - Use USER_GATE:**
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

5. **⛔ HARD STOP - Use USER_GATE:**
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
4. Re-ask USER_GATE for GREEN phase
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

4. **⛔ HARD STOP - Use USER_GATE:**
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

**bc-test automatically detects test frameworks and codeunit ranges:**

#### AL Test Framework Detection

The tool reads `app.json` to find test configuration:

```json
{
  "appId": "12345678-1234-1234-1234-123456789012",
  "name": "My App",
  "version": "1.0.0.0",
  "test": {
    "enabled": true,
    "codunitIdRanges": [
      { "from": 50100, "to": 50199 }
    ]
  }
}
```

When `test.enabled` is `true`, bc-test:
- Reads `codunitIdRanges` array
- Runs all test codeunits in those ranges
- No user input needed

```bash
# Auto-detects from app.json test.codunitIdRanges
bc-test
# Output: "Running tests 50100-50199..."
# Discovers and executes all [Test] procedures
```

#### External Test Framework Detection

For non-AL projects, bc-test detects external frameworks:

```bash
# Detects pytest from pytest.ini
bc-test
# Output: "Detected pytest framework"
# Runs: pytest --tb=short -v
# Results written to bc-test.log

# Detects Jest from jest.config.js or package.json
bc-test
# Output: "Detected Jest framework"
# Runs: npm test -- --testResultsProcessor=...
# Results written to bc-test.log

# Detects Go testing from go.mod
bc-test
# Output: "Detected Go testing"
# Runs: go test ./... -v
# Results written to bc-test.log
```

#### Fallback Logic

If auto-detection fails, bc-test tries fallback patterns:

```bash
# Fallback order (stops at first match):
1. app.json test.codunitIdRanges (AL)
2. pytest.ini present → pytest
3. jest.config.js present → npm test
4. go.mod present → go test
5. Makefile with "test" target → make test
6. Error: No test configuration found
```

#### Benefits

- No need to remember codeunit IDs or framework names
- Works across projects automatically
- Updates when app.json changes
- Handles both AL and external frameworks transparently

### File Output Options

**Write detailed results to file instead of flooding console:**

#### AL Test Framework Output Structure

When running AL tests via bc-test, the tool produces multiple output files:

```bash
# Text format with full call stacks and error details
bc-test -o .dev/test-results.txt
# Creates: .dev/test-results.txt

# JSON format for machine-readable parsing
bc-test -o .dev/test-results.json -f json
# Creates: .dev/test-results.json

# XML format compatible with CI/CD systems
bc-test -o .dev/test-results.xml -f xml
# Creates: .dev/test-results.xml

# Console shows summary only:
# Passed: 558, Failed: 9, Skipped: 2
```

#### .dev/ Naming Convention

Test runs coexist without overwriting by using timestamped filenames:

```bash
# Pattern: {DATE}-tdd-{FRAMEWORK}-{OUTPUT_TYPE}.{EXT}

# AL tests (multiple runs, different phases)
.dev/2026-05-22-tdd-al-red.txt           # RED phase results
.dev/2026-05-22-tdd-al-green.txt         # GREEN phase results
.dev/2026-05-22-tdd-al-refactor.txt      # REFACTOR phase results

# External framework tests
.dev/2026-05-22-tdd-pytest-results.json  # pytest JSON output
.dev/2026-05-22-tdd-jest-results.json    # Jest JSON output
.dev/2026-05-22-tdd-go-results.txt       # Go test output

# Command to use dynamic dates
bc-test -o ".dev/$(date +%Y-%m-%d)-tdd-al-results.txt"
```

#### AL Test Summary Format

Example test-summary.txt structure:

```
TEST EXECUTION REPORT
=====================
Date: 2026-05-22T14:30:45Z
Framework: AL Test Framework
Total Tests Run: 567
Passed: 558
Failed: 9
Skipped: 0
Duration: 2.45 minutes

SUMMARY BY CODEUNIT:
  Codeunit 50100 "Credit Limit Tests": 8 passed, 0 failed
  Codeunit 50101 "Payment Processing Tests": 10 passed, 2 failed
  Codeunit 50102 "Invoice Tests": 540 passed, 7 failed

FAILED TESTS:
  [50101] Test_PaymentProcessing_InvalidAmountThrowsError
    Error: Expected validation error, got success
    Call Stack: [line 45 in PaymentValidator.al]
  [50102] Test_Invoice_RoundingEdgeCase
    Error: Expected 99.99, got 100.00
    Call Stack: [line 78 in InvoiceCalculator.al]
```

#### External Framework Output

Example pytest output format:

```
test-results.json (pytest):
{
  "tests": [
    {
      "nodeid": "tests/test_credit_limit.py::test_within_limit",
      "outcome": "passed",
      "duration": 0.025
    },
    {
      "nodeid": "tests/test_credit_limit.py::test_exceeds_limit",
      "outcome": "failed",
      "duration": 0.031,
      "call": "AssertionError: expected True, got False"
    }
  ],
  "summary": {
    "passed": 45,
    "failed": 2,
    "skipped": 0,
    "duration": 1.23
  }
}
```

#### JSON Structure (AL Tests)

```json
{
  "total_tests_run": 567,
  "passed": 558,
  "failed": 9,
  "skipped": 0,
  "execution_time_seconds": 147.3,
  "showing": "all",
  "tests": [
    {
      "codeunitId": 50100,
      "codeunitName": "Credit Limit Tests",
      "functionName": "Test_ValidateCreditLimit_WithinLimit",
      "success": true,
      "errorMessage": "",
      "callStack": ""
    },
    {
      "codeunitId": 50101,
      "codeunitName": "Payment Processing Tests",
      "functionName": "Test_PaymentProcessing_InvalidAmountThrowsError",
      "success": false,
      "errorMessage": "Expected validation error, got success",
      "callStack": "PaymentValidator.al:45"
    }
  ]
}
```

#### Multiple Test Runs Coexist

Each test phase and framework produces separate files — no overwrites:

```
.dev/
  2026-05-22-tdd-al-red.txt              # RED phase (test fails)
  2026-05-22-tdd-al-green.txt            # GREEN phase (test passes)
  2026-05-22-tdd-al-refactor.txt         # REFACTOR phase (all pass)
  2026-05-22-tdd-pytest-unit.json        # Unit tests
  2026-05-22-tdd-pytest-integration.json # Integration tests
  2026-05-22-tdd-jest-unit.json          # JS unit tests
```

### Failures-Only Filter

**Focus on what needs attention during development:**

#### Full Run vs Failures-Only Commands

```bash
# FULL RUN: See all test results (recommended for initial verification)
bc-test
# Output:
# Passed: 558
# Failed: 9
# Skipped: 0
# Details for all 567 tests...

# FAILURES-ONLY: See only the 9 failures (recommended for iterative fixes)
bc-test --failures-only
# Output:
# 9 failures (out of 567 total)
# [50101] Test_PaymentProcessing_InvalidAmountThrowsError
#   Error: Expected validation error, got success
#   Call Stack: PaymentValidator.al:45
# [50102] Test_Invoice_RoundingEdgeCase
#   Error: Expected 99.99, got 100.00
#   Call Stack: InvoiceCalculator.al:78
# ... (8 more failures)

# FILE OUTPUT: Failures-only for archival
bc-test -o .dev/failures.txt --failures-only
# File contains only the 9 failures with full error details
```

#### Usage Heuristics

**Full run (bc-test) is used when:**
- First test verification after RED phase (confirm 1 test fails)
- After GREEN phase (confirm 1 test passes)
- After REFACTOR phase (confirm all tests still pass)
- Before commit (final verification)
- CI/CD pipelines (complete record required)

Example workflow:
```bash
# RED phase: verify test fails
bc-test  # Full run → shows "Passed: 0, Failed: 1"

# GREEN phase: verify test passes
bc-test  # Full run → shows "Passed: 1, Failed: 0"

# REFACTOR phase: verify all still pass
bc-test  # Full run → shows "Passed: 567, Failed: 0"
```

**Failures-only (bc-test --failures-only) is used when:**
- Iterating on a fix (after seeing failure, fixing code, testing again)
- Large test suite with only a few failures
- During development to reduce console noise
- Focusing on specific broken tests

Example workflow:
```bash
# Initial failure
bc-test --failures-only
# Output: "9 failures (out of 567 total)"

# Fix first failure in PaymentValidator.al
# Test again
bc-test --failures-only
# Output: "8 failures (out of 567 total)" ← PaymentValidator fix worked

# Fix second failure
bc-test --failures-only
# Output: "7 failures (out of 567 total)"
```

#### Recommended Development Cycle

```
FULL RUN (verify failure)
  ↓
FAILURES-ONLY (identify what failed)
  ↓
FIX CODE (address first failure)
  ↓
FAILURES-ONLY (quick check progress)
  ↓
FAILURES-ONLY (check next failure)
  ↓
FIX CODE (address second failure)
  ↓
FULL RUN (final verification before commit)
```

This pattern balances speed during development with thorough verification before commit.

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

**Automate test execution in GitHub Actions and Azure Pipelines:**

#### GitHub Actions Integration

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup AL Development Environment
        run: |
          choco install bc-dev-tools
      
      - name: Run Tests
        run: |
          bc-test -o test-results.json -f json
        shell: pwsh
      
      - name: Check for Failures
        run: |
          $results = Get-Content test-results.json | ConvertFrom-Json
          if ($results.failed -gt 0) {
            Write-Error "$($results.failed) tests failed"
            exit 1
          }
      
      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: test-results.xml
          check_name: AL Test Results
          comment_title: Test Summary
```

Result: GitHub shows test failures in PR checks, blocks merge until passing.

#### Azure Pipelines Integration

```yaml
# azure-pipelines.yml
trigger:
  - main
  - develop

pr:
  - main

pool:
  vmImage: 'windows-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.9'
  displayName: 'Use Python 3.9'

- task: PowerShell@2
  displayName: 'Compile AL App'
  inputs:
    targetType: 'inline'
    script: |
      al-compile --output compile-errors.log
      if ($LASTEXITCODE -ne 0) {
        Write-Error "Compilation failed"
        exit 1
      }

- task: PowerShell@2
  displayName: 'Run Tests'
  inputs:
    targetType: 'inline'
    script: |
      bc-test -o test-results.xml -f xml
      if ($LASTEXITCODE -ne 0) {
        Write-Error "Tests failed"
        exit 1
      }

- task: PublishTestResults@2
  displayName: 'Publish Test Results'
  condition: always()
  inputs:
    testResultsFormat: 'NUnit'
    testResultsFiles: 'test-results.xml'
    testRunTitle: 'AL Tests'
    failTaskOnFailedTests: true
```

Result: Azure Pipelines shows test pass/fail in build logs and blocks merge until passing.

#### JSON-Based Verification

```bash
# Export test results for CI/CD parsing
bc-test -o test-results.json -f json

# Parse with jq for failed tests
jq '.tests[] | select(.success == false)' test-results.json

# Check if any tests failed
if jq -e '.failed > 0' test-results.json; then
  echo "Tests failed!"
  exit 1
fi

# Generate summary for build logs
jq '{
  total: .total_tests_run,
  passed: .passed,
  failed: .failed,
  duration: .execution_time_seconds
}' test-results.json
```

#### CI/CD Workflow Result

Both GitHub and Azure show:
- Test execution status in PR checks
- Pass/fail count in build summary
- Individual test failure details
- Merge blocked until all tests pass

Example PR check output:
```
✓ Test (1 check)
  AL Test Results
    Passed: 558
    Failed: 9
    Duration: 2m 45s
    
    Failed Tests:
    - Test_PaymentProcessing_InvalidAmountThrowsError
    - Test_Invoice_RoundingEdgeCase
    - ... (7 more)
```

### Example Workflows

#### Scenario 1: New Feature (Red-Green-Refactor Cycle)

**Goal:** Add credit limit validation for customer orders

**RED Phase:**
```bash
# 1. Write failing test
cat > src/Tests.al <<'EOF'
codeunit 50200 "Credit Limit Tests"
{
    Subtype = Test;

    [Test]
    procedure Test_Order_WithinCreditLimit_Allowed()
    var
        Validator: Codeunit "Credit Limit Validator";
        Result: Boolean;
    begin
        // [GIVEN] Customer with 10000 limit, 5000 outstanding
        Result := Validator.ValidateCreditLimit('C001', 3000);
        
        // [THEN] Should allow (5000 + 3000 = 8000 < 10000)
        Assert.IsTrue(Result, 'Should allow order within limit');
    end;
}
EOF

# 2. Compile and test
al-compile
bc-publish

# 3. Run test - should FAIL
bc-test -o ".dev/$(date +%Y-%m-%d)-tdd-al-red.txt"
# Output: "Passed: 0, Failed: 1" ✓ RED phase verified
```

**GREEN Phase:**
```bash
# 1. Implement production code
cat > src/CreditLimitValidator.al <<'EOF'
codeunit 50100 "Credit Limit Validator"
{
    procedure ValidateCreditLimit(
        CustomerNo: Code[20];
        OrderAmount: Decimal
    ): Boolean
    var
        Customer: Record Customer;
        Outstanding: Decimal;
    begin
        if not Customer.Get(CustomerNo) then
            Error('Customer not found');

        if Customer."Credit Limit (LCY)" = 0 then
            exit(true); // Unlimited

        Outstanding := GetOutstandingAmount(CustomerNo);
        exit(Outstanding + OrderAmount <= Customer."Credit Limit (LCY)");
    end;

    local procedure GetOutstandingAmount(CustomerNo: Code[20]): Decimal
    var
        SalesHeader: Record "Sales Header";
        Outstanding: Decimal;
    begin
        SalesHeader.SetRange("Sell-to Customer No.", CustomerNo);
        SalesHeader.SetFilter(Status, '<>%1', SalesHeader.Status::Released);
        if SalesHeader.FindSet() then
            repeat
                Outstanding += SalesHeader."Amount Including VAT";
            until SalesHeader.Next() = 0;
        exit(Outstanding);
    end;
}
EOF

# 2. Compile and test
al-compile
bc-publish

# 3. Run test - should PASS
bc-test -o ".dev/$(date +%Y-%m-%d)-tdd-al-green.txt"
# Output: "Passed: 1, Failed: 0" ✓ GREEN phase verified
```

**REFACTOR Phase:**
```bash
# 1. Improve code quality
cat > src/CreditLimitValidator.al <<'EOF'
codeunit 50100 "Credit Limit Validator"
{
    /// <summary>
    /// Validates that a new order does not exceed customer credit limit.
    /// </summary>
    procedure ValidateCreditLimit(
        CustomerNo: Code[20];
        OrderAmount: Decimal
    ): Boolean
    var
        Customer: Record Customer;
    begin
        Customer := GetCustomer(CustomerNo);

        if IsUnlimitedCredit(Customer) then
            exit(true);

        exit(IsWithinCreditLimit(Customer, OrderAmount));
    end;

    local procedure GetCustomer(CustomerNo: Code[20]): Record Customer
    var
        Customer: Record Customer;
    begin
        if not Customer.Get(CustomerNo) then
            Error('Customer not found');
        exit(Customer);
    end;

    local procedure IsUnlimitedCredit(Customer: Record Customer): Boolean
    begin
        exit(Customer."Credit Limit (LCY)" = 0);
    end;

    local procedure IsWithinCreditLimit(
        Customer: Record Customer;
        OrderAmount: Decimal
    ): Boolean
    var
        Outstanding: Decimal;
    begin
        Outstanding := GetOutstandingAmount(Customer."No.");
        exit(Outstanding + OrderAmount <= Customer."Credit Limit (LCY)");
    end;

    local procedure GetOutstandingAmount(CustomerNo: Code[20]): Decimal
    var
        SalesHeader: Record "Sales Header";
        Outstanding: Decimal;
    begin
        SalesHeader.SetRange("Sell-to Customer No.", CustomerNo);
        SalesHeader.SetFilter(Status, '<>%1', SalesHeader.Status::Released);
        if SalesHeader.FindSet() then
            repeat
                Outstanding += SalesHeader."Amount Including VAT";
            until SalesHeader.Next() = 0;
        exit(Outstanding);
    end;
}
EOF

# 2. Compile and run ALL tests
al-compile
bc-publish

bc-test -o ".dev/$(date +%Y-%m-%d)-tdd-al-refactor.txt"
# Output: "Passed: 1, Failed: 0" ✓ REFACTOR phase verified
# No regressions introduced
```

#### Scenario 2: Bug Fix with Test

**Goal:** Fix rounding bug in invoice calculator

**Quick Development Cycle:**
```bash
# 1. Write failing test for the bug
bc-test  # Run all first
# Output shows: Test_Invoice_RoundingEdgeCase FAILED
# Error: Expected 99.99, got 100.00

# 2. Look at failures only
bc-test --failures-only
# Output: Only the rounding edge case failure (faster iteration)

# 3. Fix the rounding logic
# ... edit InvoiceCalculator.al ...

# 4. Quick check with failures-only
bc-test --failures-only
# Output: "1 failures (out of 567 total)" ← Still broken

# 5. Fix again
# ... adjust decimal rounding ...

# 6. Quick check again
bc-test --failures-only
# Output: "0 failures (out of 567 total)" ✓ Bug fixed!

# 7. Final full verification
bc-test -o ".dev/$(date +%Y-%m-%d)-tdd-al-bugfix.txt"
# Output: "Passed: 567, Failed: 0" ✓ All tests pass, no regressions
```

#### Scenario 3: Refactor with Safety Net

**Goal:** Optimize payment processing without breaking behavior

**Comprehensive Workflow:**
```bash
# 0. Baseline: verify all tests pass
bc-test -o ".dev/$(date +%Y-%m-%d)-tdd-al-baseline.txt"
# Output: "Passed: 567, Failed: 0"
# (Baseline file acts as safety net)

# 1. Refactor payment processing
# Extract duplicate validation logic
# Improve variable names
# Add XML documentation
# ... complex refactoring ...

# 2. Compile
al-compile
# Output: No errors

# 3. Publish
bc-publish
# Output: App published successfully

# 4. Run full test suite
bc-test -o ".dev/$(date +%Y-%m-%d)-tdd-al-after-refactor.txt"
# Output: "Passed: 565, Failed: 2"
# ⚠️ Refactoring broke 2 tests!

# 5. Identify failures
bc-test --failures-only
# Output shows which 2 tests broke

# 6. Revert refactoring
# git checkout src/PaymentProcessor.al
# (Or manually revert changes)

# 7. Verify revert
bc-test -o ".dev/$(date +%Y-%m-%d)-tdd-al-reverted.txt"
# Output: "Passed: 567, Failed: 0" ✓ Back to safe state

# 8. Document and continue
# Add note to code: "Refactoring reverted - broke payment tests"
# Try different refactoring approach
```

#### Test Phases Summary

All three scenarios follow this pattern:

```
WRITE → COMPILE → PUBLISH → TEST → GATE → ITERATE
  ↓       ↓         ↓        ↓     ↓      ↓
Code  Compiles  Updates  Runs  User    Next
      OK        Server   OK    Reviews Cycle
```

Each phase is gated by user verification of test results before proceeding.

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
