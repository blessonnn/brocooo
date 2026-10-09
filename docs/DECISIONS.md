# Brocooo — Architecture & Design Decisions

> Auto-maintained log of every non-obvious choice made during development.

## D001 — Monorepo structure
**Decision**: pnpm workspace + Turborepo with `apps/web`, `apps/api`, `apps/worker`, `packages/caption-styles`.
**Why**: Keeps frontend and backend in sync, shared types via the caption-styles package, and Turbo handles build ordering. No Nx overhead.

## D002 — SQLite-backed job queue (not Celery)
**Decision**: Use a `jobs` table in SQLite polled by the worker process instead of Celery + Redis.
**Why**: Zero-infrastructure requirement for dev/self-host. The worker polls every 1s, claims a job with an atomic UPDATE, and runs the pipeline. Interface is abstract enough to swap to Celery later.

## D003 — LLM provider failover chain
**Decision**: Gemini Flash (free tier) → Groq Llama (free tier) → local Ollama. Automatic failover on 429/5xx.
**Why**: Guarantees the app always works — online with free APIs, or fully offline with Ollama. JSON schema enforcement + retry with exponential backoff on rate limits.

## D004 — Caption rendering: ASS + libass
**Decision**: Generate ASS subtitle files and burn with FFmpeg `libass` filter, not custom video frame manipulation.
**Why**: ASS supports karaoke timing (`\k` tags), transforms (`\fscx`, `\fscy`), colors, fonts — everything needed for all 40+ styles. Rendering is GPU-accelerated by libass and doesn't require Python per-frame processing. Canvas preview in browser uses the same JSON style definition for parity.

## D005 — Face detection: MediaPipe over YOLO
**Decision**: Use MediaPipe Face Detection (BlazeFace) as primary, with OpenCV YuNet as fallback.
**Why**: MediaPipe runs efficiently on CPU, has good accuracy for reframing, and doesn't need model downloads beyond pip install. YOLO-nano kept as optional for object tracking in gaming/sports genres.

## D006 — TTS: Kokoro-82M primary, Piper fallback
**Decision**: Kokoro for higher quality, Piper for speed and wider language support.
**Why**: Both are fully local/free. Kokoro-82M produces natural speech quality comparable to commercial TTS. Piper covers 30+ languages with ONNX models. User can pick in settings.

## D007 — Dark theme with lime accent
**Decision**: Dark background (#0A0A0F), card surfaces (#141419), lime accent (#C6FF3D), with HSL-based palette.
**Why**: Matches the snazo-style reference. Lime on dark is high contrast, energetic, and distinctive. Full light theme deferred to Phase 4.

## D008 — No credits / no paywall
**Decision**: Zero monetization code. Fair-use queue only (max 3 concurrent jobs per session, 50 jobs/day per IP).
**Why**: Core product philosophy. Fair-use prevents abuse without feeling like a limit.

## D009 — yt-dlp datacenter IP workaround
**Decision**: Three fallback strategies: (a) upload file directly, (b) user-provided cookies.txt, (c) run worker at home via Cloudflare Tunnel.
**Why**: YouTube actively blocks datacenter IPs. The app must always have a working path. Clear error messages guide users to alternatives.

## D010 — CPU-only constraint
**Decision**: All models use int8/ONNX quantization. FFmpeg uses `libx264 -preset veryfast`. Worker pool sized to `os.cpu_count() - 1`.
**Why**: Must run on a laptop with integrated GPU only. Benchmarks will be documented in README.
