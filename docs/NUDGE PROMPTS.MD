# 🎯 Rejoice Slim v2 – Wrap‑Up Nudge Prompts

Use these **at the end of a story / coding task** to make sure the agent fully closes the loop: code, tests, backlog, and documentation.

---

## 1. Post‑Implementation Checklist (for Dev Agent)

After you think the feature is done, run this checklist **before** returning the final answer:

1. **Tests & Quality**
   - Have I:
     - Run the relevant tests (`pytest` subset first, then full suite if the change is broad)?
     - Fixed or explained any failing tests?
     - Left the code formatted and lint‑clean according to the repo config?

2. **Backlog Alignment (`docs/BACKLOG.md`)**
   - For the story I just worked on:
     - Have I **updated the story’s `**Status:**`** (❌ / 🚧 / ✅) to reflect reality?
     - Have I **ticked acceptance criteria checkboxes** `[ ] → [x]` only where the behavior exists **and is tested**?
     - If I only did part of the story, did I set `Status: 🚧 In Progress` and **leave untouched** criteria as `[ ]`?
     - If I added meaningful behavior that the story didn’t mention, did I add **concrete, testable acceptance criteria or technical notes** (without changing the story text itself)?

3. **Priority Tiers & Progress Overview**
   - If this story was in an MVP/MMP tier and its status changed:
     - Do the **"📊 Progress Overview"** counts still match the actual numbers of ✅ / 🚧 / ❌ stories?
     - Do the **Priority Tiers (MVP / MMP / MLP)** still make sense given what now exists in code?
     - If I changed tiers, did I make **small, justified adjustments** rather than a big rewrite?

4. **CHANGELOG & Developer Experience**
   - For user‑visible or cross‑cutting changes:
     - Have I added an appropriate entry to `CHANGELOG.md` (Unreleased section) using the existing style?
     - Did I update or add any **relevant docs** (only when clearly needed and allowed) that explain new flags, commands, or behaviors?

5. **Final Self‑Check Before Responding**
   - Can I **name the story ID(s)** I just advanced (e.g. `[R‑003]`, `[F‑004]`)?
   - Can I point to **specific files and tests** that prove each checked criterion is real?
   - If I’m uncertain about any criterion, did I **leave it unchecked** and mention the uncertainty in my explanation (not in the files)?

---

## 2. Short Wrap‑Up Prompt (for Dev Prompt to append)

When you finish implementing a story, silently run this mental script **before** you answer:

> "Pause. I will now:
> 1) Re‑scan the relevant story in `docs/BACKLOG.md`,
> 2) Update its `**Status:**` and acceptance criteria checkboxes to reflect the actual code and tests,
> 3) Adjust the global progress numbers and, if clearly warranted, the MVP/MMP tiers,
> 4) Ensure tests pass and the change is coherent with the project’s principles (data integrity, slim, local‑first)."

Only after those 4 steps are truly done should you present your final summary and (if requested) a patch.
