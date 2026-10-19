---
name: ideate
description: Office-hours style session that pressure-tests a product idea before anything is designed or built - who has the problem, how they cope today, the narrowest version worth building and the riskiest assumptions - ending in a one-page brief and a user-interview script. Use when someone has an idea, is deciding what to build, or wants to be grilled on a plan.
argument-hint: "[idea]"
---

# Ideate

Output: `docs/ideas/<idea-slug>.md`. Do not write code, wireframes or specs
yet. The purpose of this skill is to find if the idea is worth the work. It
also finds the smallest useful version.

1. **Mode.** Ask the user which mode applies:
   - *startup*: someone must want this and pay for it.
   - *builder*: a side project, an internal tool or a project to learn. The
     result must be useful and fun.

   In builder mode, keep questions 2-4, and ask for less evidence of demand.
2. **Ask one question at a time.** Do not ask the next question before the
   user answers. If an answer is not clear, ask again. Ask for a name, a
   number or a story about an event that occurred.
   - **Demand.** Who has this problem now? Give the name of a real person or
     company. What occurred the last time that they had the problem?
   - **Status quo.** What do they do about the problem now? What is the cost
     of that in time, money or risk? To do nothing is also a competitor.
   - **Specificity.** Describe the one user who has the most need for this:
     the role, the situation, and why now.
   - **Narrowest wedge.** What is the smallest version that they will use, or
     pay for, this month?
   - **Evidence.** What did you see or hear that was a surprise to you? What
     information can change your opinion?
   - **Future fit.** If this idea works, what will it be in three years? Does
     the wedge go in that direction?

   This step is complete when each question has a concrete answer or has the
   mark "unknown".
3. **Money and trust.** Do this step only if the idea holds money, moves
   money, gives advice about money, or processes regulated data. Ask these
   questions:
   - Who holds the funds? Is a licence or a partner necessary for that?
   - How does the product earn money (fees, interchange, spread,
     subscription)? What is the margin for each transaction?
   - Where can fraud, chargebacks and disputes occur?
   - Which actions are irreversible?
4. **Challenge.** Give your honest opinion:
   - the strongest reason that this idea will work
   - the strongest reason that this idea will fail
   - one different way to think about the idea that is worth attention

   Do not make your opinion less direct.
5. **Assumptions.** Put the three to five assumptions with the highest risk
   in order. For each assumption, write the test with the lowest cost that
   can prove it wrong in two weeks.
6. **Interview script.** Write five to eight questions about past behaviour
   ("tell me about the last time…", "what did you try?", "what did it
   cost?"). Do not write questions that ask for opinions about the idea
   ("would you use this?").
7. **Write** the brief from the template. Then agree the next step with the
   user: interview users, `wireframe`, `spec`, think again, or stop.
   This step is complete when the user selects the next step.

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

After the interviews, add the findings to the evidence log. Update the
result of each assumption, and examine the decision again. The `spec` skill
reads this brief and traces its stories to the brief.

Sources: questioning style after garrytan/gstack `office-hours` (forcing
questions, paraphrased); interview approach after Rob Fitzpatrick's *The Mom
Test*; SWEBOK Requirements 3 (elicitation) and Economics.
