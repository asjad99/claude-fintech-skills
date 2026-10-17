---
name: review-thesis
description: Get an independent maker-checker review of a proposed investment verdict - a separate reviewer re-derives the key numbers from raw sources, re-runs the calculations, attacks the thesis, and approves or rejects it in the ledger. Use before treating any verdict as final, or when asked to double-check or challenge an analysis.
argument-hint: "[ledger KEY]"
---

# Independent review (maker-checker)

The author of a decision cannot approve it; the ledger enforces this by
refusing a `review` whose actor equals the decision's actor.

1. Confirm there is a proposed decision:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" --root "${user_config.research_dir}" list -s KEY --type decision`
2. Launch the `thesis-checker` agent with only: the KEY, the research folder
   path `${user_config.research_dir}`, the decision id, and the required margin
   of safety `${user_config.required_margin_of_safety_pct}`. Do not pass your
   reasoning, conversation history or hoped-for outcome; the reviewer works
   from the ledger, the raw payloads and the report, so it isn't grading its
   own work.
3. Relay its outcome and findings to the user verbatim in substance.
4. If rejected: fix each finding (new facts, superseding corrections, revised
   assumptions, rewritten report sections), propose a new decision with
   `decide`, and request a fresh review. Never edit the rejected decision.
