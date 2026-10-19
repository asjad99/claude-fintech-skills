# Design

1. **Read the code.** Read the modules that the spec has an effect on, and
   their callers. For each module, write one line about its function. Read
   the domain packs that the spec identifies.
   This step is complete when each acceptance criterion has a related module.
2. **Options.** Write two or three options. Usually, these are the smallest
   change, the cleanest design and an option between the two. For each
   option, write what changes, the effort, the risk and the cost to reverse.
   Recommend one option and give the reason.
   This step is complete when the user selects an option.
3. **Failure modes.** Examine each external call or money movement in the
   selected option. For each one, write one line for each of these failures:
   - timeout
   - duplicate
   - out-of-order
   - partial success
   - provider down

   On each line, write what the system does.
   This step is complete when each line has an answer or an open question.
4. **Threats.** For new endpoints, data stores or money flows, do a short
   STRIDE analysis. Examine spoofing, tampering, repudiation, information
   disclosure, denial of service and elevation of privilege. Record the data
   classification and where the data must be.
5. **Record.** If the decision has a high cost to reverse, write
   `docs/adr/NNNN-<title>.md` from the template below. Add new domain terms to
   `GLOSSARY.md` as `Term: one-line definition`. Create these files only when
   you have content for them.
6. **Seams.** Make a list of the public interfaces where the tests will run.
   For each interface, write one line about the errors that it finds and the
   errors that it does not find. If possible, use the seams that exist now.
   This step is complete when the user agrees.
7. **Model complex behaviour.** Some items have three or more states or two or
   more parties. Examples are a payment lifecycle, a loan and an approval workflow.
   For these items, put a Mermaid state diagram or sequence diagram in the
   ADR or the spec.

Before you launch a new money flow or provider, also do a premortem. For
this analysis, it is three months after the launch, and the flow or provider lost
money.
Make a list of the three most probable causes and the safeguard for each
cause. If a cause has no safeguard, the launch must not occur.

## Checks for every design
- Design principles:
  - abstraction, separation of concerns, modularity, encapsulation
  - interface separate from implementation, low coupling, high cohesion
  - uniformity, completeness against the spec, verifiability
- If possible, use deep modules: much behaviour behind a small interface.
- Quality attributes: money correctness, idempotency, auditability,
  resumability, security, performance, testability.
- Rules: `${CLAUDE_PLUGIN_ROOT}/references/fintech-rules.md` and the domain
  packs in `${CLAUDE_PLUGIN_ROOT}/references/domains/`. If the change has an
  effect on stores, events or pipelines, also use
  `references/data-layer.md`.
- If there is no code or stack yet, run `architect` first.

## ADR template
@@CODE1@@
ADRs are append-only. If a decision changes, write a new ADR that supersedes
the old ADR.

@@SOURCES@@
