# Igrish — Development Roadmap (tasks.md)

Companion document to `context.md` (read that first for *why*; this file is *what, in what order, in what size pieces*).

This file is written to be executed by an autonomous coding agent (Antigravity running Gemini Pro, connected to this repo via GitHub/Docker), one small task at a time, with GitHub branches as the unit of work — but it's equally usable by a human. **Software only. No Raspberry Pi, ESP32, PCB, smart home, robotics, or IoT hardware in this repo.**

---

## 0. Agent Operating Protocol — READ THIS FIRST, EVERY TIME

There are **two tracking files**, used together, at two different levels of granularity:
- **`tasks.md` (this file)** — tracks whole tasks. A checkbox here flips only when an entire task (all sub-steps + its Test) is done.
- **`progress.md`** — tracks the *sub-steps inside whichever task is currently in flight*. This is the file that protects you against power/connectivity loss, because it's updated after every small sub-step, not just at the end of a task.

Follow this procedure at the start of every work session, with no exceptions:

1. **Read `context.md` in full.** It is the source of truth for *why*; never contradict it. If a task below seems to conflict with `context.md`, `context.md` wins — stop and flag the conflict instead of guessing.
2. **Read this file (`tasks.md`) in full**, top to bottom, not just the section you think you left off at.
3. **Read `progress.md` in full.** Its `CURRENT TASK` block tells you immediately whether a task is already mid-flight.
4. **If `progress.md`'s `CURRENT TASK` block is populated** (a previous session started something and was interrupted): this is the resume case.
   - Check out the branch named in that block.
   - Run `git log` on that branch and compare its actual commits against the sub-step checkboxes in the block.
   - If they match, resume from the first unticked sub-step.
   - If they don't match (e.g., a commit landed but the checkbox update didn't, because the interruption happened in between), **trust `git log` over the ticks** — update the ticks in `progress.md` to reflect reality first, then continue.
   - If the branch is missing or unrecoverable, note that in `progress.md` under the current task, then restart that task's sub-steps from scratch.
   - Do not re-do sub-steps that are genuinely already committed and pushed.
5. **If `progress.md`'s `CURRENT TASK` block says `(none...)`:** no task is mid-flight. Find the first task in `tasks.md`, in order, whose checkbox is `[ ]`. This is the only task to work on this session — never jump ahead to a later unchecked task even if it looks easier, dependencies are ordered for a reason.
6. **Before writing any code, re-confirm the task's Dependencies (in `tasks.md`) are all checked `[x]`.** If not, stop — go complete those first, in order.
7. **Create (or check out) the exact branch named in the task** (`Branch:` field). One branch per task, never multiple tasks on one branch.
8. **Break the task into 3–7 small sub-steps** and write them into `progress.md`'s `CURRENT TASK` block as a checklist, along with the task ID and branch name, **before writing any code.** Commit and push this planning step alone first (`docs: start <task-id>, plan sub-steps`) — so even a crash before any real code is written leaves a clear trail.
9. **Work through the sub-steps one at a time.** After completing each individual sub-step:
   - Commit that sub-step's change with a small, scoped commit message.
   - **Push the branch to the remote immediately** — do not wait until the task is fully done. This is the step that actually protects you from power loss: once pushed, the work is safe on GitHub even if the local machine loses power or the container restarts.
   - Tick that sub-step's checkbox in `progress.md`'s `CURRENT TASK` block, and push that update too (fold it into the same commit as the sub-step if convenient, or a follow-up tiny commit — either is fine, as long as it's pushed before moving to the next sub-step).
10. **Once every sub-step is ticked, run the task's Test** (from `tasks.md`) before considering it done.
11. **Commit using the exact message given in `tasks.md`** (or a close variant with the same Conventional Commits prefix) for the task as a whole, open a PR from the task branch, merge once CI is green.
12. **Update `tasks.md`:** flip the task's checkbox from `[ ]` to `[x]`. Commit and push that (`docs: mark <task-id> done`).
13. **Update `progress.md`:** move the finished task's sub-step checklist into the `History` section at the bottom (mark it `COMPLETE`), and reset the `CURRENT TASK` block back to `(none — read tasks.md for the next unchecked task)`. Commit and push that too.
14. **If interrupted at any point** (power loss, connection drop, anything) — because of step 9's discipline, the worst case is losing whatever wasn't yet committed+pushed as its own sub-step. The next session's step 4 handles the rest automatically. There is no separate "emergency save" step needed if sub-steps have genuinely been committed and pushed one at a time as described.
15. **Never mark a task `[x]` in `tasks.md` unless its Test step actually passed.** A task that "mostly works" stays unflipped, with `progress.md` still reflecting it as the current in-flight task.
16. **Never skip a checkbox/ledger update.** The ticks are the only thing a resuming session trusts — inaccurate ticks are worse than no ticks. When in doubt, `git log` the branch and make the ledger match reality rather than guessing.

### Checkbox states in this file
`[ ]` not started. `[x]` fully done, Test passed. `[~]` deliberately partial/deferred (e.g., a feature shipped without one hard sub-part, per an explicit note in the task) — this is a considered decision, not a power-loss artifact. **Ordinary mid-task interruption (power loss, etc.) is never represented here** — it's tracked in `progress.md`'s `CURRENT TASK` block instead, at the sub-step level, so a resume never depends on guessing what "in progress" meant.

### Branch naming convention
`stage-<N>/<task-id>-<short-slug>` — e.g. `stage-0/t0.1-repo-scaffold`, `stage-3/t3.2-openai-adapter`.

### Task ID convention
`T<stage>.<index>` — e.g. `T0.1`, `T5.4`. IDs are stable once written; never renumber existing tasks, only append.

---

## Stage 0 — Development Environment
*Goal: a reproducible dev environment exists; nothing product-specific yet.*

- [x] **T0.1 — Repo scaffold**
  Branch: `stage-0/t0.1-repo-scaffold`
  Do: Create the full folder structure from `context.md` §4 with empty placeholder files (`.gitkeep` where needed) — `companion-app/`, `melissa-service/`, `shared/`, `docs/`, `scripts/`, `.github/workflows/`, `docker/`.
  Dependencies: none.
  Test: directory listing matches `context.md` §4.
  Commit: `chore: scaffold repo folder structure`

- [x] **T0.2 — Python service skeleton**
  Branch: `stage-0/t0.2-python-skeleton`
  Do: Initialize `melissa-service/pyproject.toml` (FastAPI, uvicorn, pytest, ruff, black, mypy as dev deps). Create `app/main.py` with a FastAPI app exposing `GET /health` → `{"status": "ok"}`.
  Dependencies: T0.1.
  Test: `uvicorn app.main:app` runs; `curl localhost:8000/health` returns 200 and the expected body.
  Commit: `feat: add melissa-service skeleton with health endpoint`

- [~] **T0.3 — Tauri shell skeleton**
  Branch: `stage-0/t0.3-tauri-skeleton`
  Do: Scaffold a blank Tauri + React app in `companion-app/` (default template is fine — no custom UI yet).
  Dependencies: T0.1.
  Test: `pnpm tauri dev` opens an empty window with no console errors.
  Commit: `feat: add companion-app tauri skeleton`

- [x] **T0.4 — CI pipeline**
  Branch: `stage-0/t0.4-ci`
  Do: Add `.github/workflows/ci.yml` running lint (`ruff`, `black --check`, `mypy`) + `pytest` for `melissa-service`, and `cargo clippy`/`rustfmt --check` + `pnpm build` for `companion-app`, on every push/PR.
  Dependencies: T0.2, T0.3.
  Test: a PR with a trivial passing test shows green CI; a PR with a deliberately broken lint rule shows red CI (verify both, then revert the deliberate break).
  Commit: `chore: add CI workflow for both apps`

- [~] **T0.5 — Local dev orchestration script**
  Branch: `stage-0/t0.5-dev-script`
  Do: Write `scripts/dev.ps1` (and/or `dev.sh`) that starts `uvicorn` and `pnpm tauri dev` together, with clear console output labeling which process is which.
  Dependencies: T0.2, T0.3.
  Test: running the script boots both processes; the Tauri window opens and `/health` responds while it's running; stopping the script cleanly stops both.
  Commit: `chore: add local dev orchestration script`

**Stage 0 Definition of Done:** all T0.x checked; a fresh clone + one script launches both processes with a working health check and green CI.

---

## Stage 1 — Basic Voice Assistant (loopback, no AI yet)
*Goal: prove the raw audio pipeline (STT + TTS) before adding intelligence.*

- [x] **T1.1 — STT/TTS port interfaces**
  Branch: `stage-1/t1.1-stt-tts-ports`
  Do: Define `ports/stt.py` (`STTProvider.transcribe(audio) -> str`) and `ports/tts.py` (`TTSProvider.synthesize(text) -> audio`) as abstract interfaces, plus trivial fake/mock implementations for testing.
  Dependencies: T0.2.
  Test: unit tests instantiate the fake adapters and confirm the interface contract via a round-trip of a known string.
  Commit: `feat: add STT/TTS provider interfaces with mock adapters`

- [x] **T1.2 — Whisper STT adapter**
  Branch: `stage-1/t1.2-whisper-adapter`
  Do: Implement `adapters/stt/whisper.py` (faster-whisper or whisper.cpp binding) implementing `STTProvider`.
  Dependencies: T1.1.
  Test: unit test with a short pre-recorded sample audio file transcribes to the expected text within reasonable tolerance.
  Commit: `feat: add whisper STT adapter`

- [x] **T1.3 — Piper TTS adapter**
  Branch: `stage-1/t1.3-piper-adapter`
  Do: Implement `adapters/tts/piper.py` implementing `TTSProvider`.
  Dependencies: T1.1.
  Test: unit test synthesizes a short known string and confirms non-empty, valid audio output.
  Commit: `feat: add piper TTS adapter`

- [x] **T1.4 — Push-to-talk hotkey in shell**
  Branch: `stage-1/t1.4-push-to-talk`
  Do: Add a global hotkey in the Tauri shell that starts/stops microphone capture and streams captured audio to the Melissa Service over a new endpoint.
  Dependencies: T0.3, T0.5.
  Test: holding the hotkey and speaking results in audio bytes arriving at the service (verify via a temporary debug log/endpoint).
  Commit: `feat: add push-to-talk capture in companion app`

- [x] **T1.5 — Loopback wiring (STT → TTS, no LLM)**
  Branch: `stage-1/t1.5-loopback`
  Do: Add an endpoint that takes captured audio, runs it through the Whisper adapter, immediately runs the resulting text through the Piper adapter, and returns/plays the synthesized audio — validating the full pipeline without AI logic yet.
  Dependencies: T1.2, T1.3, T1.4.
  Test: hold hotkey, say a sentence, hear it spoken back within a couple seconds, across 10 consecutive tries.
  Commit: `feat: wire STT->TTS loopback end to end`

**Stage 1 Definition of Done:** all T1.x checked; loopback works reliably (10/10 tries intelligible).

---

## Stage 2 — Wake Word
*Goal: replace push-to-talk with always-listening "Hey Melissa" / "Melissa" detection.*

- [x] **T2.1 — Wake word engine integration**
  Branch: `stage-2/t2.1-wake-word-sensor`
  Do: Integrate a lightweight local keyword-spotting model as `adapters/sensors/wake_word.py`, running continuously with negligible CPU, emitting a detection event.
  Dependencies: T0.2.
  Test: manual test confirms detection fires on "Hey Melissa"/"Melissa" and not on a set of similar-sounding control phrases (log false positive/negative rate over ~20 trials).
  Commit: `feat: add wake word detection sensor`

- [x] **T2.2 — Gate STT behind wake event**
  Branch: `stage-2/t2.2-gate-stt`
  Do: Replace the push-to-talk trigger from Stage 1 with the wake-word event as the trigger for audio capture + STT. Confirm no audio is transcribed before a wake event.
  Dependencies: T2.1, T1.5.
  Test: with wake word active, ambient conversation not containing "Melissa" produces zero STT calls (verify via log/counter); saying the wake word triggers exactly one capture window.
  Commit: `feat: gate STT capture behind wake word event`

- [x] **T2.3 — Listening UX cue**
  Branch: `stage-2/t2.3-listening-cue`
  Do: Add a short audio and/or visual cue in the Tauri shell immediately after wake detection.
  Dependencies: T2.2.
  Test: manual — cue is audible/visible within a few hundred ms of saying the wake word.
  Commit: `feat: add listening UX cue after wake detection`

- [x] **T2.4 — Mic/wake settings toggle**
  Branch: `stage-2/t2.4-mic-toggle`
  Do: Add a settings entry to fully disable always-listening; verify the wake-word sensor actually stops when disabled.
  Dependencies: T2.1.
  Test: toggling off stops the sensor process/loop verifiably (not just hides UI); toggling on resumes it.
  Commit: `feat: add mic/wake-word settings toggle`

**Stage 2 Definition of Done:** all T2.x checked; wake word reliably triggers listening; toggle verifiably disables it; idle CPU stays low.

---

## Stage 3 — Cloud AI Integration
*Goal: real generated replies via cloud LLM providers, replacing loopback.*

- [x] **T3.1 — LLMProvider interface**
  Branch: `stage-3/t3.1-llm-port`
  Do: Define `ports/llm.py`: `LLMProvider.generate(messages, stream=True) -> Response`, plus a mock adapter.
  Dependencies: T0.2.
  Test: unit test against the mock adapter confirms interface shape (messages in, response out, streaming iterator works).
  Commit: `feat: add LLMProvider interface with mock adapter`

- [x] **T3.2 — Secrets loader**
  Branch: `stage-3/t3.2-secrets-loader`
  Do: Implement a secrets loader reading API keys from the Windows Credential Manager (or an encrypted local file as fallback) — never plaintext in repo/committed config. Add `.gitignore` rules guaranteeing no key file is ever committed.
  Dependencies: T0.2.
  Test: unit test with a fake credential store; manual test confirms a real key set via the OS credential store is retrievable; confirm `git status` shows no secret file as trackable.
  Commit: `feat: add secure secrets loader`

- [x] **T3.3 — OpenAI adapter**
  Branch: `stage-3/t3.3-openai-adapter`
  Do: Implement `adapters/llm/openai.py` implementing `LLMProvider`, using the T3.2 secrets loader.
  Dependencies: T3.1, T3.2.
  Test: live smoke test — a real prompt returns a real completion; unit test with recorded/mocked HTTP response covers parsing.
  Commit: `feat: add openai LLM adapter`

- [x] **T3.4 — Claude adapter**
  Branch: `stage-3/t3.4-claude-adapter`
  Do: Implement `adapters/llm/claude.py` implementing `LLMProvider`.
  Dependencies: T3.1, T3.2.
  Test: same pattern as T3.3.
  Commit: `feat: add claude LLM adapter`

- [x] **T3.5 — Gemini adapter**
  Branch: `stage-3/t3.5-gemini-adapter`
  Do: Implement `adapters/llm/gemini.py` implementing `LLMProvider`. (Note: this is the *product's* Gemini adapter, used at runtime by the app — a separate, independent piece of code from the Gemini Pro model driving Antigravity's own development work. Don't conflate the two.)
  Dependencies: T3.1, T3.2.
  Test: same pattern as T3.3.
  Commit: `feat: add gemini LLM adapter`

- [x] **T3.6 — Persona prompt builder**
  Branch: `stage-3/t3.6-prompt-builder`
  Do: Implement `core/prompt_builder.py` centralizing the Melissa persona rules (always call the user "Boss"; calm/concise/supportive tone per `context.md` §2.1) so every provider receives the same persona instructions from one place.
  Dependencies: T3.1.
  Test: unit test confirms the built prompt contains the persona rules regardless of destination provider.
  Commit: `feat: add centralized persona prompt builder`

- [x] **T3.7 — Provider selector setting**
  Branch: `stage-3/t3.7-provider-selector`
  Do: Add a settings-driven active-provider + model selector (config-driven, no code change needed to switch).
  Dependencies: T3.3, T3.4, T3.5.
  Test: switching the setting between at least two providers and re-running the same prompt produces a response via the newly selected provider (verify via provider-specific log line).
  Commit: `feat: add LLM provider/model selector setting`

- [x] **T3.8 — Full voice loop integration (wake → STT → LLM → TTS)**
  Branch: `stage-3/t3.8-voice-loop-llm`
  Do: Replace Stage 1's loopback with a real call through the active `LLMProvider` (via the prompt builder) between STT and TTS.
  Dependencies: T2.2, T3.6, T3.7.
  Test: "Hey Melissa, what's 12 times 7?" produces a real, correct, spoken answer addressing the user as Boss.
  Commit: `feat: wire full voice loop through cloud LLM`

**Stage 3 Definition of Done:** all T3.x checked; full voice loop works with at least two providers switchable via settings without code changes.

---

## Stage 4 — Conversation Engine
*Goal: multi-turn conversation with short-term context, streaming TTS, sessions.*

- [x] **T4.1 — Rolling conversation buffer**
  Branch: `stage-4/t4.1-conversation-buffer`
  Do: Implement `core/conversation.py`: an in-memory rolling buffer of the last N turns, injected into the prompt via the T3.6 builder.
  Dependencies: T3.8.
  Test: unit test confirms buffer caps at N turns (oldest dropped first); manual multi-turn test confirms a follow-up question uses prior-turn context correctly.
  Commit: `feat: add rolling conversation buffer`

- [x] **T4.2 — Sentence-level streaming TTS**
  Branch: `stage-4/t4.2-streaming-tts`
  Do: Chunk streamed LLM output on sentence boundaries and begin TTS synthesis/playback per-sentence rather than waiting for the full response.
  Dependencies: T3.8.
  Test: measure/log "time to first audio" before/after — confirm a meaningful reduction vs. non-streamed baseline; manual listen-through confirms no audible choppiness.
  Commit: `feat: add sentence-level streaming TTS`

- [x] **T4.3 — Session lifecycle**
  Branch: `stage-4/t4.3-session-lifecycle`
  Do: Implement `core/session.py`: a conversation session starts on wake, ends after a configurable silence timeout.
  Dependencies: T4.1.
  Test: unit test on the timeout logic; manual test confirms a new session starts cleanly after the timeout elapses.
  Commit: `feat: add session lifecycle management`

- [~] **T4.4 — Barge-in (interrupt) handling**
  Branch: `stage-4/t4.4-barge-in`
  Do: Detect the user speaking again while Melissa's TTS is still playing, stop playback, start a new capture. **This is the hardest task in this stage — if it's not converging, ship Stage 4 without it (mark `[~]` with a clear note) rather than block the rest of the roadmap; revisit later as a backlog item.**
  Dependencies: T2.1, T4.2.
  Test: manual test — speaking over Melissa mid-sentence stops her audio and begins a new capture within roughly a second.
  Commit: `feat: add barge-in interruption handling`

**Stage 4 Definition of Done:** T4.1–T4.3 checked (T4.4 checked if feasible, otherwise explicitly deferred with a note); a 5+ turn conversation flows naturally with streaming audio and clean session boundaries.

---

## Stage 5 — Memory
*Goal: cross-session structured + semantic memory per `context.md` §8.*

- [x] **T5.1 — Structured schema + migrations**
  Branch: `stage-5/t5.1-sql-schema`
  Do: Set up SQLite via SQLAlchemy + Alembic migrations for `goals`, `projects`, `preferences`, `habits`, `nudge_log`, `conversations`, `turns` (per `context.md` §12).
  Dependencies: T0.2.
  Test: migration runs cleanly on a fresh DB; unit tests for basic CRUD on each table.
  Commit: `feat: add structured memory schema and migrations`

- [x] **T5.2 — Semantic memory store**
  Branch: `stage-5/t5.2-semantic-store`
  Do: Set up a ChromaDB collection (`memory_semantic`) with an embedding pipeline; implement `memory/store_semantic.py` for write/query.
  Dependencies: T0.2.
  Test: unit test embeds and stores a sample turn, then retrieves it via a similar query with a plausible similarity score.
  Commit: `feat: add semantic memory store`

- [x] **T5.3 — Verbatim turn write path**
  Branch: `stage-5/t5.3-turn-write-path`
  Do: Wire every conversation turn (from Stage 4) to be written to both `turns` (SQL) and the semantic store.
  Dependencies: T5.1, T5.2, T4.1.
  Test: after a live conversation, confirm turns appear in both stores with matching content/timestamps.
  Commit: `feat: persist conversation turns to structured and semantic memory`

- [x] **T5.4 — Fact extraction step**
  Branch: `stage-5/t5.4-fact-extraction`
  Do: Implement an explicit extraction step (LLM call with a narrow, structured-output prompt) that proposes structured facts (new goal, preference, completed task) from a turn, written to the structured store only after this explicit step — never inferred silently elsewhere.
  Dependencies: T5.1, T3.6.
  Test: unit test with a scripted turn ("I want to finish my AD lab tonight") confirms a matching `goals` row is created; confirm a neutral turn ("what's the weather") creates no spurious rows.
  Commit: `feat: add structured fact extraction from conversation`

- [x] **T5.5 — Context Aggregator (read path)**
  Branch: `stage-5/t5.5-context-aggregator`
  Do: Implement `memory/context_aggregator.py`: merges top-k semantic matches + all active structured goals/tasks + a recent-turn window into the prompt, respecting a token budget.
  Dependencies: T5.3, T5.4.
  Test: unit test with fixed fake data confirms correct merge/ranking/truncation under a small token budget.
  Commit: `feat: add context aggregator for memory-augmented prompts`

- [x] **T5.6 — Wire aggregator into the live conversation loop**
  Branch: `stage-5/t5.6-aggregator-integration`
  Do: Replace the plain prompt from Stage 4 with the aggregator's memory-augmented prompt in the live voice loop.
  Dependencies: T5.5, T4.1.
  Test: state a goal in one session; in a distinct later session (restart the service to prove it's not just in-memory), ask "what was I working on" and get a correct answer.
  Commit: `feat: wire memory context aggregator into conversation loop`

- [x] **T5.7 — Memory purge action**
  Branch: `stage-5/t5.7-memory-purge`
  Do: Add a settings action that clears both structured and semantic stores on user request.
  Dependencies: T5.1, T5.2.
  Test: after purge, confirm both stores are empty and a follow-up recall question gets no false memory.
  Commit: `feat: add memory purge settings action`

**Stage 5 Definition of Done:** all T5.x checked; cross-session recall verified; purge verified to clear both stores.

---

## Stage 6 — Desktop Awareness
*Goal: opt-in sensing of what's happening on the PC, per `context.md` §10.*

- [x] **T6.1 — Sensor framework + Context Snapshot**
  Branch: `stage-6/t6.1-sensor-framework`
  Do: Define a common `ContextSensor` interface and a short-lived, in-memory Context Snapshot that sensors write into on a poll interval (no long-term persistence of raw signals).
  Dependencies: T0.2.
  Test: unit test with a fake sensor confirms the snapshot updates on the expected interval and old raw data isn't retained beyond the current snapshot.
  Commit: `feat: add context sensor framework and snapshot`

- [x] **T6.2 — Active window sensor**
  Branch: `stage-6/t6.2-active-window-sensor`
  Do: Implement `adapters/sensors/active_window.py` via Win32 APIs, reporting the active window title/process.
  Dependencies: T6.1.
  Test: unit test with mocked Win32 calls; manual test confirms switching windows updates the snapshot within one poll interval.
  Commit: `feat: add active window sensor`

- [x] **T6.3 — Process list sensor**
  Branch: `stage-6/t6.3-process-list-sensor`
  Do: Implement `adapters/sensors/process_list.py`.
  Dependencies: T6.1.
  Test: same pattern as T6.2.
  Commit: `feat: add process list sensor`

- [x] **T6.4 — Clipboard sensor**
  Branch: `stage-6/t6.4-clipboard-sensor`
  Do: Implement `adapters/sensors/clipboard.py`. Off by default (most privacy-sensitive of this batch — confirm content is used transiently only, never persisted to the snapshot's history or to disk).
  Dependencies: T6.1.
  Test: manual test confirms clipboard content is visible in the live snapshot when enabled, and confirm nothing is written to any log/DB when disabled — check disk/DB directly, don't just trust the toggle.
  Commit: `feat: add clipboard sensor (opt-in, off by default)`

- [x] **T6.5 — Input activity sensor**
  Branch: `stage-6/t6.5-input-activity-sensor`
  Do: Implement `adapters/sensors/input_activity.py` (keyboard/mouse activity, idle time).
  Dependencies: T6.1.
  Test: manual test confirms idle time increments correctly after ceasing input and resets on resuming.
  Commit: `feat: add input activity sensor`

- [x] **T6.6 — System state sensor**
  Branch: `stage-6/t6.6-system-state-sensor`
  Do: Implement `adapters/sensors/system_state.py` (CPU/system load).
  Dependencies: T6.1.
  Test: manual test confirms reported CPU usage roughly tracks Task Manager during a synthetic load.
  Commit: `feat: add system state sensor`

- [ ] **T6.7 — App/window classification table**
  Branch: `stage-6/t6.7-classification-table`
  Do: Implement `core/classification.py`: a data-driven (config file, not hardcoded logic) lookup table classifying the active app/window into coding / distraction / communication / unknown.
  Dependencies: T6.2.
  Test: unit test confirms known apps classify correctly and unknown apps fall back to `unknown` without erroring.
  Commit: `feat: add app/window classification table`

- [x] **T6.8 — Per-sensor settings toggles**
  Branch: `stage-6/t6.8-sensor-toggles`
  Do: Add individual settings toggles for each sensor from T6.2–T6.6, defaulting to the least-invasive set enabled (active app category + idle time only; clipboard/window-title detail opt-in).
  Dependencies: T6.2, T6.3, T6.4, T6.5, T6.6.
  Test: for each sensor, verifiably confirm data collection stops when its toggle is off (check the snapshot/logs directly, not just UI state) and resumes when on.
  Commit: `feat: add per-sensor settings toggles with privacy-first defaults`

- [x] **T6.9 — Wire snapshot into Context Aggregator**
  Branch: `stage-6/t6.9-aggregator-wiring`
  Do: Feed the Context Snapshot (T6.1) into the Stage 5 Context Aggregator so conversations can reference current activity.
  Dependencies: T6.1, T5.5.
  Test: "what am I working on?" produces an accurate answer based on the currently active window/project.
  Commit: `feat: wire context snapshot into memory aggregator`

**Stage 6 Definition of Done:** all T6.x checked; every sensor independently toggleable and verified off-when-disabled; Melissa correctly describes current activity when asked.

---

## Stage 7 — Productivity Companion
*Goal: contextual, non-repetitive proactive nudges, per `context.md` §3.4/§7.*

- [x] **T7.1 — Nudge cooldown log**
  Branch: `stage-7/t7.1-nudge-cooldown-log`
  Do: Implement `memory/nudge_log.py` backed by the `nudge_log` SQL table — records nudge category + timestamp + cooldown-until.
  Dependencies: T5.1.
  Test: unit test confirms a nudge category logged now correctly reports "on cooldown" until its window elapses.
  Commit: `feat: add nudge cooldown log`

- [x] **T7.2 — Heuristic decision loop (no LLM yet)**
  Branch: `stage-7/t7.2-decision-loop-heuristics`
  Do: Implement `core/decision_loop.py`: a background loop evaluating cheap heuristics on the Context Snapshot + active structured goals (e.g., N minutes in "distraction" category + an open same-day goal) to *decide whether* to nudge — deliberately no LLM call in this task, decision logic only.
  Dependencies: T6.9, T5.1, T7.1.
  Test: unit test with synthetic snapshots proves the trigger condition fires/doesn't fire correctly, and that the cooldown table correctly suppresses a repeat trigger within its window.
  Commit: `feat: add heuristic nudge decision loop`

- [x] **T7.3 — LLM nudge phrasing**
  Branch: `stage-7/t7.3-nudge-phrasing`
  Do: When the decision loop decides to nudge, generate the natural-language phrasing via the LLM (through the persona prompt builder) — the LLM's job is *only* wording, never the decision.
  Dependencies: T7.2, T3.6.
  Test: manual test confirms a triggered nudge is spoken naturally and references the actual goal/situation, not a generic template.
  Commit: `feat: add LLM-generated nudge phrasing`

- [x] **T7.4 — Nudge settings panel**
  Branch: `stage-7/t7.4-nudge-settings`
  Do: Add settings for nudge sensitivity (off / gentle / normal) and per-category mute.
  Dependencies: T7.2.
  Test: setting sensitivity to "off" verifiably stops all nudges (confirm no entries added to `nudge_log` during a test period); per-category mute suppresses only that category.
  Commit: `feat: add nudge sensitivity and mute settings`

**Stage 7 Definition of Done:** all T7.x checked; a real dogfood session produces contextual nudges with zero repeats within a cooldown window (verified via `nudge_log`).

---

## Stage 8 — Daily Briefing
*Goal: dynamic, non-templated morning greeting, per `context.md` §2.1/§6.*

- [x] **T8.1 — Briefing data-pull query**
  Branch: `stage-8/t8.1-briefing-data-pull`
  Do: Implement `core/briefing.py`'s data layer: pull active goals, yesterday's unfinished items, and stated priorities from structured memory.
  Dependencies: T5.1.
  Test: unit test against a seeded test DB confirms the correct set of goals/items is returned.
  Commit: `feat: add daily briefing data pull`

- [ ] **T8.2 — Briefing prompt + manual trigger**
  Branch: `stage-8/t8.2-briefing-prompt-manual`
  Do: Build the briefing-specific LLM prompt (via the persona builder) and add a manual "Melissa, brief me" voice/UI trigger for testing/on-demand use.
  Dependencies: T8.1, T3.6.
  Test: triggering manually across different days produces briefings that reference real, current data and don't read as templated.
  Commit: `feat: add daily briefing prompt with manual trigger`

- [ ] **T8.3 — First-activity-of-day scheduler**
  Branch: `stage-8/t8.3-first-activity-scheduler`
  Do: Implement `core/scheduler.py`: trigger the briefing automatically on the first detected activity of a new day (not a wall-clock timer, so it isn't missed if the machine was off/asleep).
  Dependencies: T8.2, T6.9.
  Test: manual test across a couple of real days confirms exactly one automatic briefing per day, on first activity, no duplicates.
  Commit: `feat: add first-activity-of-day briefing scheduler`

**Stage 8 Definition of Done:** all T8.x checked; five consecutive real mornings produce accurate, non-templated briefings.

---

## Stage 9 — Coding Companion (first plugin)
*Goal: project-aware coding help, per `context.md` §11.*

- [ ] **T9.1 — Plugin base interface**
  Branch: `stage-9/t9.1-plugin-base`
  Do: Implement `plugins/base.py`: the plugin contract (contributes context facts, optional LLM tools, optional proactive triggers with their own cooldowns), plus a plugin loader in `core/`.
  Dependencies: T5.5, T7.2.
  Test: unit test loads a trivial dummy plugin and confirms it's discoverable/registered correctly.
  Commit: `feat: add plugin base interface and loader`

- [ ] **T9.2 — VS Code project detection**
  Branch: `stage-9/t9.2-project-detection`
  Do: Implement project detection inside `plugins/coding_companion/` using the Stage 6 sensors (active window/process) to identify the current VS Code project/folder.
  Dependencies: T9.1, T6.9.
  Test: manual test across a few different open projects confirms correct project name/path is reported.
  Commit: `feat: add coding companion project detection`

- [ ] **T9.3 — Debugging/explain tool**
  Branch: `stage-9/t9.3-debug-explain-tool`
  Do: Add a tool the LLM can call (or a direct voice command) to explain a pasted/captured error or a given file, using the active project context from T9.2.
  Dependencies: T9.2, T3.7.
  Test: manual test with a real bug in a real project — response correctly references the actual project/error.
  Commit: `feat: add coding companion debug/explain tool`

- [ ] **T9.4 — Scoped documentation search tool**
  Branch: `stage-9/t9.4-doc-search-tool`
  Do: Add a narrowly-scoped "search documentation" tool exposed to the LLM (not a general web browser — keep scope tight to doc lookups for this stage).
  Dependencies: T9.1, T3.7.
  Test: manual test — a documentation question during a coding session returns a relevant, correctly scoped result.
  Commit: `feat: add scoped documentation search tool`

- [ ] **T9.5 — Focus-mode gating (shared with nudges)**
  Branch: `stage-9/t9.5-focus-mode-gating`
  Do: Implement a focus-mode signal (sustained typing activity + no idle gaps) as a shared piece of the Context Snapshot, and gate *both* the coding plugin's proactive suggestions and the Stage 7 nudge decision loop behind it — implement once, reference from both, per `context.md` §11.
  Dependencies: T9.2, T7.2, T6.5.
  Test: during a measured sustained-typing session, confirm zero proactive nudges/suggestions fire; confirm they resume once focus mode ends.
  Commit: `feat: add shared focus-mode gating for nudges and coding suggestions`

**Stage 9 Definition of Done:** all T9.x checked; useful help given in at least 3 real debugging sessions; zero interruptions logged during measured focus periods.

- [ ] **T9.6 (backlog, follow-on) — Cybersecurity Companion plugin**
  Branch: `stage-9/t9.6-cybersecurity-plugin`
  Do: Build `plugins/cybersecurity_companion/` following the exact same pattern as T9.1–T9.5 (HTB/THM/AD-lab/CTF/Linux/Windows-Internals/networking/web-security/OSINT/reverse-engineering awareness per `context.md` §2.3 item 8), reusing the plugin base interface as-is.
  Dependencies: T9.1 (do not block Stage 10 on this — safe to defer past Stage 10/11 if time-constrained, since it's structurally identical to a proven pattern).
  Test: same shape as T9.2–T9.4, applied to a real HTB/THM/lab session.
  Commit: `feat: add cybersecurity companion plugin`

---

## Stage 10 — Packaging
*Goal: one installer, not "run two dev servers."*

- [ ] **T10.1 — Bundle Melissa Service as a standalone executable**
  Branch: `stage-10/t10.1-bundle-service`
  Do: Package `melissa-service` via PyInstaller (or embedded Python) so end users don't need a separate Python install.
  Dependencies: all Stage 0–9 tasks in-scope for this release (T9.6 may remain open per its note).
  Test: the bundled executable runs standalone on a machine without a dev Python environment and passes the `/health` check.
  Commit: `chore: bundle melissa-service as standalone executable`

- [ ] **T10.2 — Tauri installer configuration**
  Branch: `stage-10/t10.2-tauri-installer`
  Do: Configure the Tauri bundler to produce a Windows installer that also installs/launches the bundled service from T10.1.
  Dependencies: T10.1.
  Test: installer runs on a clean Windows VM/account and results in both processes present and runnable.
  Commit: `chore: configure tauri windows installer`

- [ ] **T10.3 — Tray icon, auto-start, quit/restart**
  Branch: `stage-10/t10.3-tray-autostart`
  Do: Add a proper tray icon with quit/restart/settings actions and an optional (toggleable) auto-start on login.
  Dependencies: T10.2.
  Test: manual test of each tray action; confirm auto-start toggle actually adds/removes the login entry.
  Commit: `feat: add tray icon, auto-start, and quit/restart actions`

- [ ] **T10.4 — First-run setup wizard**
  Branch: `stage-10/t10.4-first-run-wizard`
  Do: Add a first-run wizard for API key entry (using the T3.2 secrets loader) and explicit sensor-consent choices (referencing the T6.8 toggles), so a fresh install starts neither broken nor wide open.
  Dependencies: T10.2, T3.2, T6.8.
  Test: on a clean install, the wizard runs exactly once, correctly stores the entered key, and correctly applies the chosen sensor consent defaults.
  Commit: `feat: add first-run setup wizard`

- [ ] **T10.5 — Local logging + crash handling**
  Branch: `stage-10/t10.5-logging-crash-handling`
  Do: Add local log files (no telemetry, no upload) and basic crash handling so failures are diagnosable without a dev environment.
  Dependencies: T10.1.
  Test: force a deliberate error and confirm it's captured in the local log with enough detail to diagnose, and the app doesn't silently vanish.
  Commit: `feat: add local logging and crash handling`

**Stage 10 Definition of Done:** all T10.x checked; clean-VM install → wizard → full voice loop with memory, sensing, and at least the coding plugin all work with zero dev-environment steps.

---

## Stage 11 — Beta Testing
*Goal: validate against real sustained use; produce a Phase 2 punch list.*

- [ ] **T11.1 — Daily-driver dogfood period (1–2 weeks)**
  Branch: `stage-11/t11.1-dogfood-log` (used only for the running issues log document, not code)
  Do: Use the packaged app as an actual daily driver; keep a running issues log (`docs/dogfood-log.md`) of bugs, annoying nudges, missed context, latency complaints — logged as they occur, not reconstructed from memory at the end.
  Dependencies: T10.5 (packaged, loggable build).
  Test: N/A — this task *is* the test; Definition of Done is time-based (see below).
  Commit: `docs: start dogfood issues log` (initial), then ongoing `fix:` commits as issues are found and resolved on their own small branches (create ad hoc `stage-11/fix-<slug>` branches per fix, following the same branch-per-task discipline).

- [ ] **T11.2 — Nudge/memory data review**
  Branch: `stage-11/t11.2-data-review`
  Do: Review `nudge_log` for repetition/appropriateness and tune thresholds from real data; review memory recall accuracy over the dogfood period and correct/purge any bad structured facts the extraction step got wrong.
  Dependencies: T11.1 (needs at least a week of real data).
  Test: spot-check a sample of nudges against the cooldown rule (zero violations) and a sample of structured facts against what was actually said (zero unverifiable/incorrect entries remaining).
  Commit: `fix: tune nudge thresholds from dogfood data`, `fix: correct memory extraction issues found in review`

- [ ] **T11.3 — Phase 1 retrospective**
  Branch: `stage-11/t11.3-retrospective`
  Do: Write `docs/retrospective-phase1.md`: what worked, what didn't, concrete Phase 2 priorities. Append a summary to `context.md` §17 (Open Ideas/Backlog).
  Dependencies: T11.1, T11.2.
  Test: N/A — review for completeness against the dogfood log.
  Commit: `docs: add phase 1 retrospective`

**Stage 11 Definition of Done:** all T11.x checked; two weeks of real daily use logged; retrospective written; Phase 2 priorities identified.

---

## Cross-Stage Notes for the Agent

- If a task's Test step can't be run in the current sandbox (e.g., no real microphone/webcam in a headless CI container), automate what can be automated, clearly note in the PR description which parts require a manual pass on the actual target machine, and leave the checkbox as `[~]` until a human/manual pass confirms it — never mark `[x]` on unverifiable claims.
- Prefer shipping a reduced version of a task over skipping it (see T4.4's fallback) — but always leave a clear note rather than silently under-delivering.
- Never renumber or delete existing task IDs, even if a task turns out unnecessary — mark it `[x]` with a one-line note ("not needed because...") instead, so history stays legible to whichever agent/human reads it next.
- Camera/webcam sensing (`context.md` §10.1) is intentionally not scheduled as a numbered task yet — it's a documented future extension point. When it's time to build it, append a new `T6.x` (or a new stage) rather than retrofitting it into an earlier task.
- Local-LLM/GPU support (`context.md` §6/§18) is intentionally not scheduled — when a GPU is added, append a new task for an Ollama-based `LLMProvider` adapter (same pattern as T3.3–T3.5) rather than modifying the existing cloud adapters.