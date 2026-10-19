# STE conversion of the SKILL.md files

The 11 files in `plugins/fintech-software-engineer/skills/*/SKILL.md` are
written in ASD-STE100 Simplified Technical English, at the practical level:
all the STE writing rules, plus a project glossary for vocabulary.

| File | Purpose |
|---|---|
| `glossary.md` | The rules, what does not change, technical names, technical verbs and words not to use |
| `ste_check.py` | Checks the measurable STE rules. Run `python3 ste/ste_check.py` from the repo root |
| `new/<skill>.md` | The source text of each converted file, with placeholders |
| `assemble.py` | Builds each SKILL.md from `new/` and copies the frontmatter, code blocks and Sources paragraph from `originals/` |
| `originals/` | The 11 SKILL.md files before the conversion |

## How to change a skill

1. Edit the SKILL.md file directly, or edit `new/<skill>.md` and run
   `python3 ste/assemble.py <skill>`.
2. Run `python3 ste/ste_check.py`. Correct each finding. "passive?" lines
   are warnings only: passive voice is permitted in descriptive text.

If you edit a SKILL.md file directly, `assemble.py` overwrites your change
the next time you run it. Then use only one method.

## What was checked

- `ste_check.py`: 0 findings in all 11 files.
- The frontmatter, the code blocks, the inline code and the Sources
  paragraphs are the same as in the originals.
- An independent review compared each original and rewrite, step by step.
  It found 13 changes of meaning. All 13 are corrected.
- The eval suite was not run, to prevent extra cost.
