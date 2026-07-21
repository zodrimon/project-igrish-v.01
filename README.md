# Igrish

> **Note:** This project is currently under active development and is not yet finished. roninxyg is working on that.

Igrish is an always-listening, privacy-first productivity and cybersecurity companion. It is designed to run locally on your machine and assist you with daily tasks, coding, and staying focused. 

It consists of two main components:
1. **melissa-service:** A FastAPI backend that handles voice processing (STT/TTS), context awareness, LLM generation, and memory storage.
2. **companion-app:** A lightweight Tauri (Rust + React) shell that resides in your system tray and provides a push-to-talk or always-listening interface to interact with the service.

## Features
- Always-on Wake Word detection
- Cross-session memory and contextual awareness
- Desktop sensing (active window, input activity) to determine focus state
- Proactive productivity nudges
- LLM Provider abstraction supporting OpenAI, Claude, and Gemini

## Development
See `context.md` and `Tasks.md` for architectural context and current roadmap.
