# Igrish — Project Context & Knowledge Base

> **Codename:** Igrish (platform/ecosystem) · **Default personality:** Melissa
> **Phase:** 1 of N — Windows Desktop AI Companion (software only)
> **Audience:** any engineer (including future-you) who needs to understand this project without a verbal briefing.

This document is the permanent source of truth for *why* the project is built the way it is. `tasks.md` is the *how and when*. If the two ever disagree, this file wins, and `tasks.md` should be corrected.

---

## 1. Vision

Igrish is the long-term goal: a real-life AI companion in the spirit of JARVIS — eventually spanning software, a dedicated OS layer, and physical hardware. **This repository is Phase 1 only**: a Windows desktop companion, software-only, single-user (you), that:

- Understands what you're doing on your PC.
- Talks naturally, in voice, when addressed or when it has something genuinely useful to say.
- Remembers your goals, projects, and habits, and gets more useful over time.
- Behaves like a calm colleague sitting next to you, not a notification system.

Everything downstream (mobile companion, hardware device, smart home, robotics) is explicitly **out of scope** for Phase 1, but the architecture below is chosen so none of those future directions require a rewrite — only new adapters/plugins.

### 1.1 Non-goals for this phase
No Raspberry Pi, ESP32, custom PCB, smart home, robotics, IoT, or physical device work happens in this repo. If a task description drifts toward any of these, stop and push it into a future-phase backlog note instead of building it.

## 2. Product Definition

### 2.1 Personality — Melissa
- Calm, intelligent, concise, supportive, occasionally humorous, professional, emotionally aware without simulating humanity.
- Always addresses the user as **"Boss"**.
- Speaks only when it adds value — she observes and understands continuously, but interrupts rarely and never repetitively. "Ambient, not intrusive" is the design test for every user-facing feature: if a feature can't pass that test, redesign it before shipping.
- Tone is generated dynamically from memory + context, never from fixed templates. Templates are allowed as a fallback when the LLM call fails, never as the primary path.

### 2.2 Target users
- **Now:** single user (Boss).
- **Later:** developers, students, cybersecurity learners, researchers, power users.
- **Eventually:** a commercial desktop product.
Because "eventually commercial," every design decision below defaults to the option that scales to multi-user / multi-tenant later, even though Phase 1 hard-codes a single user.

### 2.3 Core feature set (Phase 1 scope)
1. Wake word ("Hey Melissa" / "Melissa")
2. Natural conversation via cloud LLMs (OpenAI, Claude, Gemini), swappable
3. Long-term memory (goals, projects, preferences, coding style, habits, history)
4. Desktop awareness (active app/window, VS Code project, terminal activity, clipboard, idle time, input activity, CPU/system state) — privacy-first, opt-in per signal
5. Productivity companion (gentle, contextual, non-repetitive nudges)
6. Daily companion (dynamic morning briefing)
7. Coding companion (debugging help, explanations, doc search, idea generation, focus-aware silence)
8. Cybersecurity companion (HTB/THM/AD labs/CTF/Linux/Windows Internals/networking/web security/OSINT/reverse engineering awareness) — additive on top of the coding companion, not a separate brain
9. Premium, swappable voice (TTS abstraction)
10. Architecture that doesn't block the future Igrish ecosystem (device, OS, hardware, robotics, vision)

---

## 3. Architecture Overview

### 3.1 Guiding principle: hexagonal / ports-and-adapters
Every external capability (LLM provider, TTS engine, STT engine, OS-level sensing, storage backend) is defined as an **interface (port)** in the core, with one or more **adapters** implementing it. The core (conversation engine, memory manager, decision/orchestration logic) never imports a vendor SDK directly — it depends only on the interface. This is the single decision that makes "swap OpenAI for local Llama" or "swap Windows sensing for Linux sensing" a matter of writing a new adapter, not rewriting the app.

```
                     ┌─────────────────────────────────────────┐
                     │              Melissa Core                │
                     │  (orchestrator, decision loop, persona)   │
                     └───────────────┬───────────────────────────┘
                                      │  interfaces (ports)
        ┌───────────────┬────────────┼────────────┬───────────────┬──────────────┐
        │               │            │            │               │              │
   LLMProvider     TTSProvider   STTProvider  MemoryStore   ContextSensor   PluginHost
        │               │            │            │               │              │
  ┌─────┴─────┐   ┌─────┴─────┐ ┌────┴────┐  ┌────┴─────┐  ┌──────┴──────┐ ┌─────┴─────┐
  │OpenAI     │   │Piper      │ │Whisper  │  │SQLite    │  │Win32 hooks  │ │future:     │
  │Claude     │   │ElevenLabs │ │Azure STT│  │Chroma/   │  │VS Code ext  │ │HTB plugin  │
  │Gemini     │   │(swap-in)  │ │(swap-in)│  │Qdrant    │  │Clipboard    │ │AD-lab      │
  │Ollama(fut)│   └───────────┘ └─────────┘  │Postgres  │  │Process list │ │plugin, etc.│
  └───────────┘                              │(future)  │  └─────────────┘ └────────────┘
                                              └──────────┘
```

### 3.2 Process/service layout
- **Companion App (Tauri, Rust shell + web UI):** tray icon, overlay window, settings UI, always-running lightweight process. Chosen over Electron for lower idle RAM/CPU footprint, which matters because this process runs 24/7 in the background.
- **Melissa Service (Python, FastAPI):** the "brain" — conversation engine, memory manager, context aggregator, plugin host, decision loop. Runs as a local background service (localhost only, no external network exposure) that the Companion App talks to over HTTP/WebSocket.
- **Sensors (in-process modules inside the Melissa Service, or small helper processes where OS APIs require it):** desktop awareness collectors.

Why split the shell from the brain: the UI framework and AI/orchestration logic churn at different rates and are usually worked on separately; keeping them as two processes with a clean HTTP/WebSocket boundary means the brain is also independently testable, scriptable, and (later) portable to a server or a different OS without touching the UI.

### 3.3 Data flow (typical turn)
1. Wake word detected (local, always-on lightweight model) → STT begins capturing.
2. Utterance transcribed → sent to Melissa Service.
3. Context Aggregator attaches current desktop-awareness snapshot + relevant memory (retrieved via embedding search + recency/importance heuristics).
4. Orchestrator builds a prompt (persona + context + memory + user utterance) → calls active `LLMProvider`.
5. Response streamed back → sent to active `TTSProvider` → played by Companion App.
6. Conversation + any extracted facts written back to `MemoryStore` (async, non-blocking).

### 3.4 Proactive loop (separate from conversation)
A low-frequency background loop (e.g., every 30–60s, cheap heuristics first) watches context signals (idle time, app category, elapsed time in a category, calendar of stated goals) and only escalates to an LLM call when a heuristic threshold is crossed (e.g., "20+ minutes in a classified 'distraction' app AND user previously stated a goal for tonight"). This keeps token/API cost and interruption frequency low, and keeps the "never repetitive, never annoying" requirement enforceable in code (a cooldown/backoff table per nudge-category) rather than left to LLM judgment alone.

---

## 4. Folder Structure

```
igrish/
├── context.md
├── tasks.md
├── companion-app/                # Tauri shell + frontend
│   ├── src-tauri/                 # Rust: tray, window, OS integration glue
│   └── src/                       # React UI: chat overlay, settings, briefing view
├── melissa-service/               # Python FastAPI brain
│   ├── app/
│   │   ├── main.py
│   │   ├── core/                  # orchestrator, decision loop, persona/prompt builder
│   │   ├── ports/                 # abstract interfaces (LLMProvider, TTSProvider, ...)
│   │   ├── adapters/
│   │   │   ├── llm/               # openai.py, claude.py, gemini.py, ollama.py (future)
│   │   │   ├── tts/               # piper.py, elevenlabs.py (future)
│   │   │   ├── stt/               # whisper.py
│   │   │   └── sensors/           # active_window.py, clipboard.py, input_activity.py, process_list.py
│   │   ├── memory/                # memory manager, embedding store client, schemas
│   │   ├── plugins/                # plugin loader + first-party plugins (coding, cybersec)
│   │   └── api/                   # FastAPI routers
│   ├── tests/
│   └── pyproject.toml
├── shared/                        # cross-cutting schemas/types shared by app + service
├── docs/                          # ADRs, diagrams, research notes
├── scripts/                       # dev bootstrap, packaging scripts
├── .github/workflows/             # CI
└── docker/                        # local dev services (if any, e.g. Qdrant)
```

Rule of thumb: if a piece of logic talks to a vendor SDK or an OS API, it lives under `adapters/`. If it decides *what* Melissa should do, it lives under `core/`. If it's a new capability that's optional/removable, it's a plugin.

---

## 5. Design Philosophy

- **Ship a working app at every stage.** No stage ends with something that only runs in a debugger.
- **Ports before adapters.** Define the interface and a fake/mock adapter before wiring the real vendor SDK, so the core can be developed and tested without live API keys.
- **Heuristics before LLM calls** wherever a cheap deterministic check can decide (e.g., "is this app a distraction category"). Reserve LLM calls for judgment/generation, not classification that a lookup table can do.
- **Privacy is a default, not a feature.** Every desktop-awareness signal is opt-in, locally stored by default, and has a visible on/off switch. Nothing is uploaded to a cloud LLM provider unless the request genuinely needs it.
- **Silence is a feature.** The system must be able to decide *not* to speak. This is tested and reviewed with the same rigor as features that speak.
- **Plugins over branches.** Cybersecurity awareness, future domain companions, etc. are plugins with a defined interface, not `if` branches inside the core.

---

## 6. Technology Choices & Rationale

| Concern | Choice | Why |
|---|---|---|
| Companion shell | **Tauri** (Rust + web frontend) | Far lower idle memory/CPU than Electron for an always-on tray app; native Windows integration via Rust crates when needed. React knowledge is reused for the UI layer. |
| Brain/service | **Python + FastAPI** | Best ecosystem for LLM orchestration, embeddings, audio (Whisper/Piper), and OS-automation libraries (PyAutoGUI, pywin32). FastAPI gives async I/O for concurrent sensor polling + streaming LLM responses. |
| Relational storage | **SQLite** (Phase 1) → **PostgreSQL** (only if/when multi-device sync or commercial multi-user arrives) | SQLite is zero-ops for a single-user desktop app. Swapping to Postgres later is an adapter change if the data layer is written against an ORM (SQLAlchemy) from day one. |
| Vector/embedding store | **ChromaDB** (Phase 1) with an interface that would allow **Qdrant** later | Chroma is embeddable, no separate server needed, good enough for single-user memory scale. Qdrant is the upgrade path if memory scale or multi-process access becomes a bottleneck. |
| STT | **Whisper** (local, via faster-whisper or whisper.cpp) | Runs locally — no audio leaves the machine for transcription, which matters given "listens" is one of the most privacy-sensitive features in the whole app. |
| TTS | **Piper** (local, default) with a provider interface for premium cloud voices (e.g., ElevenLabs) as an opt-in swap | Piper gives a working, fully local, zero-cost voice from day one; the interface allows a "premium voice" upgrade without touching the core. |
| LLM providers | **OpenAI, Claude, Gemini** behind `LLMProvider`, **Ollama** reserved as a future local adapter | Cloud-first per the brief, but the interface is written so local models are a drop-in later — this is the most important abstraction in the whole system since it's the one most likely to change. |
| Desktop awareness | **Windows APIs** (via `pywin32`/`ctypes`) for window/process/clipboard/input; **Playwright** only if/when browser-tab-level detail is truly needed | Native Win32 hooks are cheaper and more reliable than automating a browser; Playwright is a heavier, opt-in escalation, not the default. |
| Packaging | **Tauri bundler** for the shell; **PyInstaller** (or a bundled embedded Python) for the service, orchestrated so the end user installs one app | Keeps distribution to "one installer" even though internally it's two processes. |
| CI | **GitHub Actions** | Free for a solo/small project, good Windows runner support for build/test. |

All of the above are explicitly revisitable — this table is a decision log, not a contract. When a choice changes, record why in §14 (Decision Log) rather than silently editing history.

---

## 7. Coding Standards & Naming Conventions

- **Python:** PEP 8, type hints everywhere in `core/` and `ports/`, `ruff` for lint, `black` for format, `mypy` (at least in `--strict` for `ports/` and `core/`).
- **Rust (Tauri shell):** standard `rustfmt` + `clippy` clean.
- **TypeScript/React:** ESLint + Prettier, functional components, hooks only (no class components).
- **Naming:**
  - Interfaces/ports: `XProvider` or `XSensor` (e.g., `LLMProvider`, `ActiveWindowSensor`).
  - Adapters: `<Vendor><Port>` (e.g., `OpenAILLMProvider`, `PiperTTSProvider`).
  - Memory records: typed schemas in `memory/schemas.py`, never raw dicts crossing module boundaries.
  - Plugins: `plugins/<domain>/plugin.py` exposing a single `register()` entrypoint.
- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`). Every stage in `tasks.md` maps to a small number of commits, not one giant commit.
- **Branching:** trunk-based with short-lived feature branches per task; a stage is "done" when its branch is merged and its Definition of Done is met.

---

## 8. Memory Architecture

Two tiers, matching two different retrieval needs:

1. **Structured memory (SQLite):** goals, projects, preferences, recurring tasks, habits, achievements — anything queryable/updatable as a record (e.g., "goal: finish AD lab, status: in progress, due: tonight"). This is what the daily briefing and productivity nudges query directly.
2. **Semantic memory (ChromaDB):** free-text conversation history and notes, embedded and retrieved by similarity + recency + importance score, for "does this feel relevant to right now" recall that structured queries can't express.

Write path: every conversation turn is stored verbatim (semantic store) and, when the orchestrator detects a fact worth structuring (a new goal, a stated preference, a completed task), it's also written to the structured store via an explicit extraction step — never inferred silently into structured memory without that step, so the structured data stays auditable and correctable.

Read path: the Context Aggregator (§3.3 step 3) merges (a) top-k semantic matches for the current utterance/situation, (b) all "active" structured goals/tasks, and (c) a small rolling window of recent turns, subject to a token budget, before building the prompt.

Forgetting/decay: importance-weighted decay so old, low-importance semantic entries rank lower over time rather than being deleted outright (deletion is a user-triggered privacy action, not an automatic memory-management one).

---

## 9. Conversation Architecture

- **Prompt construction** is centralized in one module (`core/prompt_builder.py`) so persona rules ("always call the user Boss," tone constraints) are enforced in exactly one place, not duplicated per provider.
- **Provider abstraction** (`LLMProvider`) exposes a single method roughly like `generate(messages, tools=None, stream=True) -> Response`, so streaming, tool-calling, and plain completion are handled uniformly regardless of vendor.
- **Turn-taking:** wake-word-initiated turns are explicit conversations; proactive nudges are a *different* code path that also goes through the same `LLMProvider` for text generation but is triggered by the decision loop, not by user speech — this distinction is architectural, not cosmetic, because it's what lets "never interrupt while deeply focused" be enforced by simply gating the proactive path on a focus signal.
- **Streaming:** responses stream token-by-token to TTS-ready sentence chunks (split on sentence boundaries) so voice playback can begin before the full response is generated.

---

## 10. Desktop Monitoring Architecture

- Each signal (active window title, process name, clipboard content, idle time, input activity, CPU/system load) is its own `ContextSensor` adapter with its own on/off toggle in settings, defaulting to the least invasive set enabled (active app category + idle time) and clipboard/window-title detail opt-in.
- Sensors write into a short-lived **Context Snapshot** (in-memory, refreshed on a poll interval, e.g. every few seconds) — raw signals are not persisted long-term; only derived, coarser facts (e.g., "spent 45 minutes in category: coding, project: igrish") get written to structured memory, and only with the relevant toggle enabled.
- Browser tab-level detail is treated as the most sensitive signal and is the one place Playwright/browser-extension integration is considered — explicitly opt-in, off by default, and documented as such in Settings.
- Classification of an app/window into a category (coding, distraction, communication, unknown) is a local lookup/heuristic table, not an LLM call, both for cost and so classification is inspectable and correctable by the user.

### 10.1 Camera (laptop webcam) — future, opt-in signal
Running on a laptop means a webcam is often physically present. A `PresenceSensor` (e.g., "is a person present / facing the screen" — coarse presence only, not identity recognition, not recording, no frames persisted to disk) is an optional future `ContextSensor`, off by default, added only once the sensor framework above is stable. It slots in exactly like any other sensor — no core changes required — and is called out here so the sensor interface (poll → derive a coarse fact → discard raw data) is designed from the start to comfortably fit a camera-based signal later without a redesign. This is still software-only: it uses whatever camera the laptop already has, not new hardware.

---

## 11. Plugin Architecture

- A plugin registers: (a) a set of domain facts/knowledge it can contribute to the Context Aggregator, (b) optional additional tools the LLM can call, (c) optional proactive triggers with their own cooldown rules.
- First-party plugins for Phase 1: `coding_companion` (project awareness, debugging helpers, doc search) and `cybersecurity_companion` (HTB/THM/AD-lab/CTF awareness) — both are plugins, not core, because both are optional lenses on top of the same orchestrator and both are exactly the kind of thing a future multi-user product would want users to enable/disable independently.
- A plugin must not import another plugin directly; cross-plugin communication goes through the core's shared context/memory, keeping plugins independently removable.

---

## 12. Database Design (high level)

**SQLite (structured):**
- `goals(id, title, status, priority, due_at, created_at, updated_at)`
- `projects(id, name, path, kind, last_active_at)`
- `preferences(key, value, updated_at)`
- `habits(id, description, cadence, last_observed_at)`
- `nudge_log(id, category, triggered_at, cooldown_until)` — powers "never repetitive."
- `conversations(id, started_at, ended_at)` / `turns(id, conversation_id, role, text, created_at)`

**ChromaDB (semantic):**
- Collection `memory_semantic`: `{id, text, embedding, metadata: {source, importance, created_at, project, tags}}`

Schema is versioned via a lightweight migration tool (e.g., `alembic` for SQLite) from the very first stage that touches the database, so schema changes are never manual/ad hoc.

---

## 13. Security & Privacy Principles

- **Local-first sensing:** raw desktop-awareness data never leaves the machine; only user utterances and the minimal context needed for a given LLM call are sent to a cloud provider, and only for that call.
- **Secrets:** API keys stored via OS credential store (Windows Credential Manager) or an encrypted local secrets file, never in plaintext config committed to the repo.
- **Local network only:** Melissa Service binds to `127.0.0.1` and is never exposed on the LAN/internet in Phase 1.
- **Explicit consent per signal:** every sensor has its own toggle, defaults to off for anything beyond "active app category" and "idle time."
- **Right to delete:** a settings action purges structured memory, semantic memory, and conversation history on request.
- **No silent telemetry.** If usage analytics are ever added (post-Phase-1, for the commercial product), they are opt-in and disclosed in this document before being built.

---

## 14. Decision Log

| Date-ish | Decision | Rationale | Status |
|---|---|---|---|
| Phase 1 kickoff | Tauri over Electron for the shell | Lower idle resource footprint for an always-on app | Active |
| Phase 1 kickoff | Python/FastAPI for the brain | Best LLM/audio ecosystem fit | Active |
| Phase 1 kickoff | SQLite + Chroma over Postgres + Qdrant | Zero-ops for single-user scale; clear upgrade path | Active |
| Phase 1 kickoff | Cloud LLMs only, local-model port reserved | Matches brief; keeps door open for Ollama later | Active |
| Phase 1 kickoff | Heuristics-first classification for context/nudges | Cost control + inspectability | Active |

(Future decisions get appended here, not substituted in place of the above.)

---

## 15. Commercial Vision (context only — not Phase 1 work)

If/when this becomes a commercial product: the single-user assumptions in §12 (one `preferences` row per key, no `user_id` columns) are the first things that need revisiting, alongside packaging as a signed installer, license/entitlement checks, and a proper telemetry/consent flow. None of this is built in Phase 1; it's recorded here so the schema and service boundaries chosen now don't accidentally foreclose it (e.g., adding a `user_id` column later should be a migration, not a rewrite).

---

## 16. Future Expansion Plan (context only)

- **Igrish Device / Igrish OS / portable companion:** the Melissa Service's HTTP/WebSocket boundary (§3.2) is the seam where a future device would attach instead of the Tauri shell.
- **Vision system / smart home / robotics:** each becomes a new `ContextSensor` or a new class of adapter/plugin — never a change to the core orchestrator's contract.

---

## 17. Open Ideas / Backlog Notes
- Local LLM adapter (Ollama) once hardware constraints/latency justify it.
- Qdrant migration if semantic memory scale outgrows Chroma.
- Browser-extension-based tab awareness as an alternative to Playwright automation (lighter weight, more explicit consent surface).
- Mobile companion app once the service boundary is stable.

---

## 18. Agent-Assisted Development Workflow

This project is being built by an autonomous coding agent (Antigravity, running Gemini Pro, connected to this GitHub repo via Docker) rather than by hand, one small task at a time. This has two consequences for how this repo is organized:

- **`tasks.md` is written as small, independently completable, checkbox-tracked tasks**, each mapped to exactly one git branch, so the agent (or a human) can always tell precisely what's done and what's next by reading the checkboxes — not by reading prose.
- **Resumability is a requirement, not a nicety.** Work can stop at any time (including mid-task, e.g., a power/connectivity interruption) and must be resumable by re-reading `context.md` + `tasks.md` and finding the first unchecked task. See the "Agent Operating Protocol" at the top of `tasks.md` for the exact procedure.

**Current inference constraint:** no local LLM/GPU yet — all LLM calls go through cloud APIs (OpenAI/Claude/Gemini) per §6. A GPU is planned for later, at which point a local-model adapter (Ollama, per §6/§16) becomes viable; nothing in the architecture should be built in a way that assumes a GPU exists until that upgrade actually happens.

## 19. Version Control & Commit Guidelines

- **Write commits like a human.** Avoid overly robotic or "AI-vibed" commit messages.
- If you create something new, simply say: `created [thing]`.
- If you update something, simply say: `updated [thing]`.
- Keep it natural, concise, and direct (e.g., `updated fast api endpoint for wake word`, `created pocketsphinx sensor`, `fixed bug in audio playback`).

---

*This file is a living document. Update it whenever an architectural decision changes — do not let `tasks.md` and reality drift ahead of what's written here.*