---
name: wireframe
description: Turn an idea brief or spec into low-fidelity wireframes - user journeys, a numbered screen inventory, and clickable screens in HTML or in Figma - including empty, loading, error and failure states. Use when someone wants to see an idea, mock up screens, sketch a flow, or prepare something to show users.
argument-hint: "[idea or spec path] [html|figma]"
---

# Wireframe

Output: `docs/wireframes/<slug>/` with `index.html` or a Figma link, plus
`screens.md`. Low fidelity on purpose: greys, real labels, no branding, so
feedback is about the flow, not the colours.

1. **Read.** The idea brief in `docs/ideas/` or the spec in `docs/specs/`.
2. **Journeys.** List the three to five journeys that matter most, each as
   numbered steps from trigger to outcome. Include the unhappy path.
   Done when the user agrees the list.
3. **Screen inventory.** Write `screens.md`: one line per screen with an id
   (W1, W2…), its purpose, the journey steps it serves and the states it
   needs: empty, loading, success, validation error, failure, no access.
4. **Choose the medium.** Ask unless the argument says:
   - **HTML**: one self-contained file, inline CSS, no external assets.
     Screens link to each other so the journey can be clicked through; a
     small index lists every screen and state.
   - **Figma**: when the Figma connector is available, load its design
     skills first and build one frame per screen, named by id. If Figma is
     not connected, say so and use HTML.
5. **Draw.** Real copy, not lorem ipsum. Each state from the inventory is
   shown, not only the happy path.
   When screens show or move money:
   - amounts always with currency; pending and available balances apart
   - fees, exchange rate and the final amount shown before confirmation
   - an explicit review-and-confirm step before anything irreversible,
     then a receipt with a reference
   - declined, failed, reversed and "price out of date" states drawn
6. **Test script.** Add to `screens.md` three to five tasks to give a user
   ("send £50 to a new payee") and what to watch for. No leading questions.
7. **Review.** Show the screens and revise.
   Done when every journey can be clicked or followed end to end and the
   user approves.

Acceptance criteria in `spec` can cite screen ids (for example "AC4 (S2,
W3)"), so each requirement traces to what the user saw.

Sources: SWEBOK Requirements 3 (elicitation, prototyping) and 5
(validation); state coverage after Nielsen's heuristics (visibility of
system status, error prevention); money screens apply the core fintech rules
on amounts, currencies and irreversible movements.
