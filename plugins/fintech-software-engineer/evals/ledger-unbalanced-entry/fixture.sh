#!/bin/bash
set -e
mkdir -p src
cat > src/Ledger.cs <<'CS'
namespace Books;

public record Entry(string Account, decimal Debit, decimal Credit);

public record Transaction(string Id, IReadOnlyList<Entry> Entries);

public class Ledger
{
    private readonly List<Entry> _entries = new();

    public void Post(Transaction tx)
    {
        _entries.AddRange(tx.Entries);
    }

    public decimal Balance(string account) =>
        _entries.Where(e => e.Account == account).Sum(e => e.Debit - e.Credit);
}
CS
