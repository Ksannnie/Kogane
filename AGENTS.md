# KOGANE AGENTS

## Project instructions

- Read the relevant project documentation before implementing changes.
- Preserve the current working commands, personality modes, and project direction.
- Make small, focused changes rather than broad rewrites.
- Write tests for new functionality and validate behavior with the existing project test suite.
- Never fabricate calendar events or personal memories using AI-generated responses.
- Use actual storage and deterministic functions for factual personal data.
- Never test against or overwrite live personal memory or schedule files.
- Never expose or commit API keys, private information, or secrets.
- Request permission before using microphones, cameras, or sensitive desktop actions.
- Keep future robot movement commands separate from conversational AI.
- Do not implement real flight control without a dedicated, validated flight controller and an explicit safety review.
- Never automatically commit or push changes without the user's approval.

## Working principles

- Prefer the existing architecture and preserve the current code structure.
- Prefer local, deterministic logic over speculative AI generation for personal facts.
- Keep the assistant persona recognizable but not excessive.
- When adding features, prefer modular implementations that fit the current project layout.
- Validate changes against the repository's current tests before claiming success.

## Safety and privacy

- Treat memory files, schedule files, app automation, and camera access as sensitive.
- Keep user data local and explicit.
- Require user consent before any microphone, camera, or system-wide action.
- Treat flight control as a separate safety-critical subsystem with independent fail-safes.

## Repo rules

- Do not overwrite existing personal data files during testing or development.
- Do not push directly to GitHub without explicit user approval.
- Keep documentation aligned with verified project behavior rather than aspirational claims.
