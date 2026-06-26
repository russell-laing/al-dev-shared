# TDD Credit Limit Worked Example

This worked example is the canonical end-to-end reference for the shared
TDD workflow. `knowledge/tdd-workflow.md` should point here instead of
embedding repeated copies of the same code blocks.

## Setup

Use a simple credit-limit validator example to demonstrate one complete
RED -> GREEN -> REFACTOR cycle.

The AL snippets are intentionally partial. They show the production validator,
test shape, and phase-specific command pattern, but a real project must supply
its own `ICustomerRepository` interface, mock repository codeunit, and test
assert library context before the snippets can compile and run.

The example assumes:

- Codeunit `50100` for the production validator.
- Codeunit `50200` for the test codeunit.
- An `ICustomerRepository` interface so tests can inject controlled customer
  and outstanding-balance data.

## RED

```al
codeunit 50100 "Credit Limit Validator"
{
    procedure ValidateCreditLimit(
        CustomerNo: Code[20];
        OrderAmount: Decimal;
        Repo: Interface ICustomerRepository
    ): Boolean
    begin
        exit(false);
    end;
}
```

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

```bash
# Compile the app
al-compile

# Publish to BC server
bc-publish

# Execute the test codeunit; the RED phase should fail
bc-test -o ".dev/$(date +%Y-%m-%d)-tdd-al-red.txt"
```

Expected summary: `Passed: 0, Failed: 1`.

## GREEN

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
        if not Repo.TryGetCustomer(CustomerNo, Customer) then
            Error('Customer not found');

        if Customer.CreditLimit = 0 then
            exit(true); // Unlimited

        Outstanding := Repo.GetOutstandingAmount(CustomerNo);
        exit(Outstanding + OrderAmount <= Customer.CreditLimit);
    end;
}
```

```bash
# Compile the app
al-compile

# Publish to BC server
bc-publish

# Execute the test codeunit; the GREEN phase should pass
bc-test -o ".dev/$(date +%Y-%m-%d)-tdd-al-green.txt"
```

Expected summary: `Passed: 1, Failed: 0`.

## REFACTOR

```al
codeunit 50100 "Credit Limit Validator"
{
    /// <summary>
    /// Validates that a new order does not exceed customer credit limit.
    /// </summary>
    procedure ValidateCreditLimit(
        CustomerNo: Code[20];
        OrderAmount: Decimal;
        Repo: Interface ICustomerRepository
    ): Boolean
    var
        Customer: Record Customer;
    begin
        Customer := GetCustomer(CustomerNo, Repo);

        if IsUnlimitedCredit(Customer) then
            exit(true);

        exit(IsWithinCreditLimit(Customer, OrderAmount, Repo));
    end;

    local procedure GetCustomer(
        CustomerNo: Code[20];
        Repo: Interface ICustomerRepository
    ): Record Customer
    var
        Customer: Record Customer;
    begin
        if not Repo.TryGetCustomer(CustomerNo, Customer) then
            Error('Customer not found');

        exit(Customer);
    end;

    local procedure IsUnlimitedCredit(Customer: Record Customer): Boolean
    begin
        exit(Customer.CreditLimit = 0);
    end;

    local procedure IsWithinCreditLimit(
        Customer: Record Customer;
        OrderAmount: Decimal;
        Repo: Interface ICustomerRepository
    ): Boolean
    var
        Outstanding: Decimal;
    begin
        Outstanding := Repo.GetOutstandingAmount(Customer."No.");
        exit(Outstanding + OrderAmount <= Customer.CreditLimit);
    end;
}
```

```bash
# Compile the app
al-compile

# Publish to BC server
bc-publish

# Execute all test codeunits to verify refactoring did not break behavior
bc-test -o ".dev/$(date +%Y-%m-%d)-tdd-al-refactor.txt"
```

Expected summary: `Passed: 1, Failed: 0`.
