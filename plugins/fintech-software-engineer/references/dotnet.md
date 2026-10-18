# .NET notes

Versions and frameworks come from the repo: `global.json`, `<TargetFramework>`
in each `.csproj`, `Directory.Build.props`, `Directory.Packages.props`. Use the
test framework and libraries the solution already uses; the names below are
defaults for a new project.

## Commands (verify they match the repo's CI)
```
dotnet build -warnaserror
dotnet test
dotnet format --verify-no-changes
dotnet list package --vulnerable --include-transitive
```

## Project settings
- `<Nullable>enable</Nullable>`, `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`,
  `<AnalysisLevel>latest-recommended</AnalysisLevel>`.
- Central package versions in `Directory.Packages.props`; lock files on
  (`RestorePackagesWithLockFile`).

## Money and dates
- `decimal` for amounts and rates; `double` only for non-money science.
- `readonly record struct Money(decimal Amount, Currency Currency)` with
  operators that reject mixed currencies.
- `Math.Round(x, 2, MidpointRounding.ToEven)`: always pass the mode.
- System.Text.Json: serialise money as a string through a converter.
- `DateOnly` for value, settlement and due dates, `DateTimeOffset` for instants,
  `TimeProvider` injected for the clock.
- EF Core: `HasPrecision(19, 4)` (or the domain's precision) on every decimal
  column; migrations committed; `AsNoTracking()` for reads.

## Code
- Guard clauses or validated value types at public boundaries.
- Catch specific exceptions; let unexpected ones surface. Use a result type
  where failure is an expected outcome (missing data, stale price).
- `async` all the way down, with `CancellationToken` passed through.
- Records for value objects; `sealed` by default.

## Tests
- xUnit with descriptive names that include the criterion id
  (`AC3_transfer_is_rejected_when_available_balance_is_too_low`).
- Attributes can't hold `decimal`: pass money cases as strings parsed with
  `CultureInfo.InvariantCulture`, or use `TheoryData<decimal, ...>`.
- FsCheck for property tests; Verify for golden outputs; Testcontainers for
  database and broker integration tests.

## Tooling
The official `csharp-lsp` plugin gives Claude diagnostics and navigation; Aaron
Stannard's `dotnet-skills` plugin has deeper .NET guidance if needed.
