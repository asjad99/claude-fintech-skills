# STE project glossary

This glossary supports the ASD-STE100 (Simplified Technical English) version
of the SKILL.md files in `plugins/fintech-software-engineer/skills/`.

The conversion uses the **practical** level: all STE writing rules, plus this
glossary for vocabulary. The words were not checked one by one against the
licensed STE dictionary.

`ste/ste_check.py` reads the tables below. It accepts the words in the
"Technical names" and "Technical verbs" tables, and it flags the words in the
"Words not to use" table.

## What does not change

- The YAML frontmatter (`name`, `description`, `argument-hint`). The
  `description` tells Claude when to use a skill. A change can stop a skill
  from starting.
- Code blocks, inline code, file paths, commands and `${CLAUDE_PLUGIN_ROOT}`.
- The templates in code blocks. They show the output, they are not
  instructions.
- Skill names, agent names and IDs: P1-P12, S1, AC1, T1, W1.
- The names of the principles (for example **Red first**, **Deep modules**).
  The README uses these names.
- The "Sources:" paragraph at the end of each file. It is a list of
  citations.
- Text in quotation marks that Claude says to a user (for example the
  interview questions).

## Rules that the files obey

| Rule | Limit |
|---|---|
| Sentence in a procedure (numbered step or list item) | 20 words or fewer |
| Descriptive sentence | 25 words or fewer |
| Paragraph | 6 sentences or fewer |
| Instructions | Command form, active voice, one instruction in each sentence |
| Conditions | Write the condition first: "If X, do Y." |
| Verb forms | Simple tenses. No -ing forms, except in technical names |
| Contractions, phrasal verbs | Do not use |
| Step results | "This step is complete when ..." (was "Done when ...") |

## Technical names

These are names of things in software engineering and finance. They are
permitted, also when they have an -ing form.

| Term | Note |
|---|---|
| acceptance criterion, criteria | A testable condition with an ID |
| ADR | Architecture decision record |
| blocking finding | A review finding that stops the merge |
| should-fix finding | A review finding that does not stop the merge |
| finding | A result of a review |
| coding agent | An AI agent that writes code |
| diff, base reference | Git terms |
| seam | A public interface where a test runs |
| vertical slice | A small change through all layers |
| walking skeleton | The smallest end-to-end system |
| kill switch | A control that stops a money flow |
| premortem | An analysis of how a launch can fail, done before the launch |
| idempotency key | A key that stops a duplicate operation |
| maker-checker | Two different people make and approve an action |
| ledger, journal entry | Accounting records |
| day-count convention | A rule to calculate interest for a period |
| rounding, rounding mode, rounding midpoint | Money calculation terms |
| coupling, cohesion | Design properties of modules |
| accounting, trading, testing, lending | Business and engineering areas |
| compensating record | A new record that corrects an incorrect record |
| floating point | A binary number type that is not exact for money |
| clearing, authorisation | Stages of a card payment |
| structured logging, logging | Logs with named fields |
| event sourcing | A write model that stores events |
| change data capture | A method to copy database changes |
| hosting, messaging | Infrastructure categories |
| spoofing, tampering | STRIDE threat categories |
| loading, pending | Names of UI states and balance states |
| branding | Logos and brand colours |
| number parsing | Conversion of text to numbers |
| happy path, unhappy path | The flow with no errors, and the flows with errors |
| flaky test | A test that sometimes passes and sometimes fails |
| red, green | A test that fails, a test that passes |

## Technical verbs

These verbs are for computer processes and software work.

| Verb | Note |
|---|---|
| run, build, test, debug, review, fix | |
| commit, merge, push, tag, rewrite (history) | Git |
| deploy, release, ship, publish | |
| migrate, persist, reconcile, redact | |
| lint, format, refactor, bisect | |
| validate, approve, assign, deny | |
| create, delete, install, load, link, export | |
| log, scan, lock, seed, inject, replay | |
| delegate | Give a task to an agent |
| supersede | One ADR replaces an older ADR |

## Words not to use

| Do not use | Use |
|---|---|
| choose, chose, chosen | select, selected |
| prefer | use ... if possible |
| ensure | make sure |
| needs, need to | must, is necessary |
| handle, handles | process, do |
| skim | read quickly |
| bump | increase |
| pin | identify |
| grade | examine |
| grill | question |
| roughly | approximately |
| typically | usually |
| via | through |
| vs | and, compared with |
| e.g., i.e., etc. | for example, that is |
| cope | what they do about the problem |
| soften | make less direct |
| cheap, cheapest | with the lowest cost |
| boring | well-known |
| thinnest, plainest | smallest, most simple |
| try, tried | do, did |
| reduce | decrease |
| happen, happens, happened | occur, occurs, occurred |
| unless | if ... not |
| whether | if |
| avoid | do not, prevent |
| halt | stop |
| touch, touches | have an effect on, be about |
| crosses | goes through, changes more than one |
| thus | so that, because of this |
