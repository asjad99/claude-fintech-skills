---
name: ideate
description: Office-hours style session that pressure-tests a product idea before anything is designed or built - who has the problem, how they cope today, the narrowest version worth building and the riskiest assumptions - ending in a one-page brief and a user-interview script. Use when someone has an idea, is deciding what to build, or wants to be grilled on a plan.
argument-hint: "[idea]"
---

# Ideate

Output: `docs/ideas/<idea-slug>.md`. No code, wireframes or specs yet: the
job is to find out whether this is worth building and what the smallest
worthwhile version is.

1. **Mode.** Ask which fits: *startup* (someone must want and pay for this)
   or *builder* (side project, internal tool, learning; the bar is that it
   is useful and fun). Builder mode keeps questions 2-4 and goes lighter on
   demand evidence.
2. **Ask, one question at a time.** Wait for each answer. Push back on
   vague ones: ask for a name, a number or a story that already happened.
   - **Demand.** Who has this problem now? Name a real person or company.
     What happened the last time they hit it?
   - **Status quo.** How do they cope today, and what does that cost in
     time, money or risk? Doing nothing is a competitor too.
   - **Specificity.** Describe the one user who needs this most: role,
     situation, why now.
   - **Narrowest wedge.** What is the smallest version they would use, or
     pay for, this month?
   - **Evidence.** What have you seen or heard that surprised you? What
     would change your mind?
   - **Future fit.** If this works, what does it look like in three years,
     and does the wedge lead there?
   Done when each question has a concrete answer or is marked unknown.
3. **Money and trust** (only when the idea holds, moves or advises on
   money, or handles regulated data). Who holds the funds, and does that
   need a licence or partner? How does it earn (fees, interchange, spread,
   subscription) and what is the margin per transaction? Where do fraud,
   chargebacks and disputes come in? Which actions can't be undone?
4. **Challenge.** Give your honest read: the strongest reason this works,
   the strongest reason it fails, and one alternative framing worth
   considering. Don't soften it.
5. **Assumptions.** Rank the three to five riskiest assumptions. For each,
   the cheapest test that could prove it wrong within two weeks.
6. **Interview script.** Five to eight questions about past behaviour
   ("tell me about the last time…", "what did you try?", "what did it
   cost?"), not opinions about the idea ("would you use this?").
7. **Write** the brief from the template and agree the next step:
   interview users, `wireframe`, `spec`, rethink, or stop.
   Done when the user has chosen.

## Template
```markdown
# <Idea>
Mode: startup | builder · Date: YYYY-MM-DD · Status: exploring

## Problem and user
## How they cope today
## Narrowest wedge
## Money and trust (if any)
## Riskiest assumptions
1. <assumption> — test: <cheapest test> — result: pending
## Interview script
## Evidence log
- YYYY-MM-DD <who> — what they said or did, quoted where possible
## Decision and next step
```

After interviews, add findings to the evidence log, update each
assumption's result and revisit the decision. `spec` reads this brief and
traces its stories back to it.

Sources: questioning style after garrytan/gstack `office-hours` (forcing
questions, paraphrased); interview approach after Rob Fitzpatrick's *The Mom
Test*; SWEBOK Requirements 3 (elicitation) and Economics.
