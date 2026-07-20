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

### T6.1 — Sensor framework + Context Snapshot
Branch: `stage-6/t6.1-sensor-framework`
Sub-steps:
- [ ] 1. Create `app/ports/sensor.py` interface.
- [ ] 2. Create `app/core/context_snapshot.py` for holding short-lived state.
- [ ] 3. Create tests.

---

## History (completed tasks — most recent first)

*(Empty. As tasks complete, append a short block here, e.g.:)*

```
### T5.7 — Memory purge action — COMPLETE
Branch: stage-5/t5.7-memory-purge (merged)
Sub-steps: 2 ticked, PR merged.
Notes: Added DELETE /api/memory to purge all structured and semantic stores.
```

```
### T5.6 — Wire aggregator into the live conversation loop — COMPLETE
Branch: stage-5/t5.6-aggregator-integration (merged)
Sub-steps: 1 ticked, PR merged.
Notes: Replaced plain prompt with the context aggregator in voice.py.
```

```
### T5.5 — Context Aggregator (read path) — COMPLETE
Branch: stage-5/t5.5-context-aggregator (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Implemented memory/context_aggregator.py to aggregate structured facts and semantic memories into the system prompt.
```

```
### T5.4 — Fact extraction step — COMPLETE
Branch: stage-5/t5.4-fact-extraction (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Added async fact extraction from user turns to populate SQL structured memory.
```

```
### T5.3 — Verbatim turn write path — COMPLETE
Branch: stage-5/t5.3-turn-write-path (merged)
Sub-steps: 2 ticked, PR merged.
Notes: Integrated SQL write path for turns along with semantic write path.
```

```
### T5.3 — Semantic retrieval in prompt — COMPLETE
Branch: stage-5/t5.3-semantic-retrieval (merged)
Sub-steps: 2 ticked, PR merged.
Notes: Integrated ChromaDB retrieval into system prompt and voice loop.
```

```
### T5.2 — Semantic memory store — COMPLETE
Branch: stage-5/t5.2-semantic-store (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Added ChromaDB-backed semantic memory store and tests.
```

```
### T5.1 — Structured schema + migrations — COMPLETE
Branch: stage-5/t5.1-sql-schema (merged)
Sub-steps: 4 ticked, PR merged.
Notes: Added SQLAlchemy models, Alembic migrations, and SQLite DB setup.
```

```
### T4.3 — Session lifecycle — COMPLETE
Branch: stage-4/t4.3-session-lifecycle (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Added conversation session lifecycle with inactivity timeout.
```

```
### T4.2 — Sentence-level streaming TTS — COMPLETE
Branch: stage-4/t4.2-streaming-tts (merged)
Sub-steps: 2 ticked, PR merged.
Notes: Added streaming TTS, yielding audio chunks as the LLM generates sentences.
```

```
### T4.1 — Rolling conversation buffer — COMPLETE
Branch: stage-4/t4.1-conversation-buffer (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Added in-memory rolling conversation buffer for short-term context.
```

```
### T3.8 — Full voice loop integration — COMPLETE
Branch: stage-3/t3.8-voice-loop-llm (merged)
Sub-steps: 2 ticked, PR merged.
Notes: Integrated STT -> LLM -> TTS in the backend voice stream endpoint.
```

```
### T3.7 — Provider selector setting — COMPLETE
Branch: stage-3/t3.7-provider-selector (merged)
Sub-steps: 2 ticked, PR merged.
Notes: Added LLM registry to provide the active LLMProvider.
```

```
### T3.6 — Persona prompt builder — COMPLETE
Branch: stage-3/t3.6-prompt-builder (merged)
Sub-steps: 2 ticked, PR merged.
Notes: Added prompt builder with system persona prompt.
```

```
### T3.5 — Gemini adapter — COMPLETE
Branch: stage-3/t3.5-gemini-adapter (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Added Gemini LLM provider implementation.
```

```
### T3.4 — Claude adapter — COMPLETE
Branch: stage-3/t3.4-claude-adapter (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Added Claude LLM provider implementation.
```

```
### T3.3 — OpenAI adapter — COMPLETE
Branch: stage-3/t3.3-openai-adapter (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Added OpenAI LLM provider implementation.
```

```
### T3.2 — Secrets loader — COMPLETE
Branch: stage-3/t3.2-secrets-loader (merged)
Sub-steps: 4 ticked, PR merged.
Notes: Added keyring and python-dotenv based secure secrets loader.
```

```
### T3.1 — LLMProvider interface — COMPLETE
Branch: stage-3/t3.1-llm-port (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Added LLMProvider abstract base class and a MockLLMAdapter for testing.
```

```
### T2.4 — Mic/wake settings toggle — COMPLETE
Branch: stage-2/t2.4-mic-toggle (merged)
Sub-steps: 2 ticked, PR merged.
Notes: Added backend and frontend toggle to enable/disable wake word sensor.
```

```
### T2.3 — Listening UX cue — COMPLETE
Branch: stage-2/t2.3-listening-cue (merged)
Sub-steps: 2 ticked, PR merged.
Notes: Added visual pulsing animation during audio capture.
```

```
### T2.2 — Gate STT behind wake event — COMPLETE
Branch: stage-2/t2.2-gate-stt (merged)
Sub-steps: 3 ticked, PR merged.
Notes: SSE endpoint established. React app captures audio when wake word is detected.
```

```
### T2.1 — Wake word engine integration — COMPLETE
Branch: stage-2/t2.1-wake-word-sensor (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Added pocketsphinx wake word sensor triggered on 'melissa'.
```

```
### T1.5 — Loopback wiring (STT → TTS, no LLM) — COMPLETE
Branch: stage-1/t1.5-loopback (merged)
Sub-steps: 2 ticked, PR merged.
Notes: Fast API returns synth audio chunk via Piper, React plays it back successfully. Loopback proven.
```

```
### T1.4 — Push-to-talk hotkey in shell — COMPLETE
Branch: stage-1/t1.4-push-to-talk (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Added React mic recording and FastAPI voice stream receiver endpoint.
```

```
### T1.3 — Piper TTS adapter — COMPLETE
Branch: stage-1/t1.3-piper-adapter (merged)
Sub-steps: 3 ticked, PR merged.
Notes: piper-tts adapter created and unit tested to generate WAV bytes.
```

```
### T1.2 — Whisper STT adapter — COMPLETE
Branch: stage-1/t1.2-whisper-adapter (merged)
Sub-steps: 3 ticked, PR merged.
Notes: faster-whisper adapter created and unit tested with sample audio.
```

```
### T1.1 — STT/TTS port interfaces — COMPLETE
Branch: stage-1/t1.1-stt-tts-ports (merged)
Sub-steps: 3 ticked, PR merged.
Notes: Basic abstract classes and mock adapters created.
```

```
### T0.5 — Local dev orchestration script — COMPLETE (Unverifiable)
Branch: stage-0/t0.5-dev-script (merged)
Sub-steps: 1 ticked, 2 unverifiable.
Notes: Unverifiable in sandbox as Tauri dev requires MSVC for Rust GUI.
```

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