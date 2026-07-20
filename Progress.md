# Igrish — Live Progress Ledger (progress.md)

This file is the **single source of truth for "exactly where things stand right now."** `tasks.md` tracks which whole tasks are done (`[x]`) — this file tracks the *sub-steps inside the current task*, updated far more often, so that a power/connectivity loss never costs more than a few minutes of work.

**This file is append-only in spirit:** don't delete old entries. When a task finishes, its entries stay as history (useful for the Stage 11 retrospective) — only the "CURRENT TASK" block at the top ever gets overwritten.

---

## HOW TO USE THIS FILE (read this every session, before touching code)

1. This file always has exactly one **`## CURRENT TASK`** block. It tells you the task ID, its branch, and a sub-step checklist for that task specifically.
2. **Before starting any task**, break it into 3–7 small sub-steps (e.g., for `T3.3 — OpenAI adapter`: "1. write ports-conformant class skeleton, 2. implement non-streaming call, 3. implement streaming, 4. unit test with mocked response, 5. live smoke test, 6. wire into provider registry"). Write them into the CURRENT TASK block as a checklist **before writing any code.**
3. **After finishing each sub-step** (not after finishing the whole task):
   - `git add` + `git commit` (small, scoped commit — sub-step granularity, not task granularity).
   - `git push` the task branch to the remote **immediately**. Local commits alone are not safe against power loss on the machine running Antigravity — the whole point of pushing after every sub-step is that GitHub, not the local disk, becomes the durable record.
   - Tick the sub-step's checkbox in the CURRENT TASK block below.
   - Commit *this file's update* too (a tiny `docs: update progress ledger` commit is fine, or fold it into the same commit as the sub-step if convenient) and push it.
4. **This means every sub-step = one commit = one push = one ticked box.** Never batch multiple sub-steps into a single push "to be efficient" — the whole design trades a few extra small commits for never losing more than one sub-step of work.
5. **When the whole task is done** (all sub-steps ticked, Test passed per `tasks.md`): follow `tasks.md` §0 step 9–10 (commit, PR, merge, tick the task in `tasks.md`), then replace the CURRENT TASK block below with `(none — read tasks.md for the next unchecked task)` and push that too.
6. **If a session starts and finds a populated CURRENT TASK block:** that's the resume signal. Check out its branch, `git log` it to see which sub-step commits actually landed, cross-check against which sub-step boxes are ticked below (they should match — if they don't, trust `git log`, not the ticks, and fix the ticks first), and continue from the first unticked sub-step. Do not restart finished sub-steps.
7. **If the branch has commits that aren't reflected as ticked sub-steps** (e.g., a crash happened between pushing code and updating this file), reconcile this file to match the real branch state before writing any new code.

---

## CURRENT TASK

### T0.5 — Local dev orchestration script
Branch: `stage-0/t0.5-dev-script`
Sub-steps:
- [x] 1. Write `scripts/dev.ps1` to start FastAPI and Tauri apps concurrently.
- [~] 2. Test running `dev.ps1` and verify both processes start. *(Unverifiable in sandbox due to MSVC)*
- [~] 3. Verify that stopping the script cleanly shuts down both processes. *(Unverifiable)*

---

## History (completed tasks — most recent first)

*(Empty. As tasks complete, append a short block here, e.g.:)*

```
### T0.4 — CI pipeline — COMPLETE
Branch: stage-0/t0.4-ci (merged)
Sub-steps: 4 ticked, PR merged.
Notes: CI verified with intentional breakage and fix.
```

```
### T0.3 — Tauri shell skeleton — COMPLETE (Unverifiable)
Branch: stage-0/t0.3-tauri-skeleton (merged)
Sub-steps: 3 ticked, 1 marked unverifiable.
Notes: Rust requires MSVC which was not available in this sandbox. User needs to run `pnpm tauri dev` locally to test.
```

```
### T0.2 — Python service skeleton — COMPLETE
Branch: stage-0/t0.2-python-skeleton (merged)
Sub-steps: all 3 ticked, all pushed, PR merged.
Notes: none.
```

```
### T0.1 — Repo scaffold — COMPLETE
Branch: stage-0/t0.1-repo-scaffold (merged)
Sub-steps: all 5 ticked, all pushed, PR merged.
Notes: none.
```