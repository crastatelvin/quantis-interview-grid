# Quantis Interview Grid

An AI-powered interview simulator that turns job descriptions into tailored mock interviews with per-answer scoring and a final coaching report.

## Why this name
`Quantis Interview Grid` is unique, memorable, and aligns with the product vision:
- **Quantis** -> quantified performance and scoring intelligence
- **Grid** -> structured simulation environment and progress tracking

## Production v1 Scope
- FastAPI backend with typed request/response models
- Role-aware interview setup from job description text
- Per-answer evaluation across 5 weighted dimensions
- Final report generation with consolidated coaching insights
- React frontend shell for setup, interview, and report flow

## Improvements over handoff blueprint
- JSON-first prompting/parsing to reduce LLM format breakage
- Input validation with Pydantic models and constrained values
- Session TTL cleanup to avoid unbounded in-memory growth
- Safer fallback behavior when model output is malformed
- CORS configuration via environment variables
- Clear separation of scoring logic from AI generation
- Groq API integration (OpenAI-compatible client), no Gemini dependency

## Next recommended features
- Auth + persistent user history
- Retry/backoff and circuit breaker for LLM calls
- Observability (structured logs, traces, latency dashboards)
- Voice mode (STT + TTS) with optional accessibility captions
- Resume upload and JD-match gap analysis

