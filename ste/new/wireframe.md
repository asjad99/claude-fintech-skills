# Wireframe

Output: `docs/wireframes/<slug>/` with `index.html` or a Figma link, and
`screens.md`. The fidelity is low intentionally: grey colours, real labels
and no branding. The feedback is then about the flow, not about the colours.

1. **Read.** Read the idea brief in `docs/ideas/` or the spec in
   `docs/specs/`.
2. **Journeys.** Make a list of the three to five most important journeys.
   Write each journey as numbered steps, from the trigger to the outcome.
   Include the unhappy path.
   This step is complete when the user agrees with the list.
3. **Screen inventory.** Write `screens.md` with one line for each screen.
   Each line contains:
   - an ID (W1, W2…)
   - the purpose of the screen
   - the journey steps that the screen is for
   - the states that the screen must have: empty, loading, success,
     validation error, failure, no access
4. **Select the medium.** If the argument does not give the medium, ask the
   user:
   - **HTML**: Make one self-contained file, with inline CSS and no external
     assets. Link the screens to each other, so that a person can click
     through the journey. Add a small index that shows each screen and state.
   - **Figma**: If the Figma connector is available, load its design skills
     first. Build one frame for each screen, and use the screen ID as the
     frame name. If Figma is not connected, tell the user and use HTML.
5. **Draw.** Use real text, not lorem ipsum. Show each state from the
   inventory, not only the happy path.
   If screens show or move money, obey these rules:
   - Always show amounts with their currency. Show pending balances and
     available balances separately.
   - Before confirmation, show the fees, the exchange rate and the final
     amount.
   - Before an irreversible action, add a step where the user examines and
     confirms the action. After the action, show a receipt with a reference.
   - Draw the states for declined, failed, reversed and "price out of date".
6. **Test script.** In `screens.md`, add three to five tasks to give to a
   user ("send £50 to a new payee"). For each task, write what to look for.
   Do not ask questions that suggest an answer.
7. **Review.** Show the screens to the user, and change them as necessary.
   This step is complete when these conditions are true:
   - A person can click or follow each journey from start to end.
   - The user approves.

Acceptance criteria in `spec` can refer to screen IDs (for example "AC4 (S2,
W3)"). Each requirement then traces to the screen that the user saw.

@@SOURCES@@
