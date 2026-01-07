# Prompt: Generate ONE Industry-Grade PoC from These Notes (Scope-Strict)

You are my Senior AI Engineer + Tech Lead mentor.

I already have BIG NOTES for a day above. I want ONE hands-on PoC to practice ONLY what’s in these notes (industry-grade).

## Hard rules (very important)
- The PoC MUST target ONLY the concepts/subtopics present in the BIG NOTES.
- Do NOT introduce extra technologies/topics not in the notes (no Kubernetes/Terraform/DSA/etc unless explicitly inside the notes).
- If something outside the notes could help (e.g., Docker, CI), list it ONLY under “Optional Extras” and keep the core PoC independent.
- Time-box: core PoC should be doable in **3–6 hours**.

## Your task
1) Extract the key skills from BIG NOTES and map them to a PoC goal.
2) Propose exactly **ONE** PoC (not multiple options) that is realistic and interview-worthy.
3) Provide an industry-grade deliverable spec including:

### A) PoC Overview
- Title (short)
- Problem statement (2–4 lines)
- Success criteria (5–8 checkboxes)
- What this PoC demonstrates in interviews (5–8 bullets)

### B) Scope Mapping (must be explicit)
Create a table:
- Note topic/subtopic → Where it is implemented in PoC (file/module/feature)

### C) Architecture (simple but real)
- ASCII diagram of flow
- Components & responsibilities (bullets)

### D) Repo Structure (production-like)
- A complete folder tree (src/, tests/, scripts/, configs/, docs/, etc.)
- Mention key files and what each contains

### E) Implementation Plan
- 7–12 steps in order
- Each step: what to implement + why + “done when …”

### F) Interfaces / Contracts
Depending on notes:
- If API-focused: endpoint specs (method, path, request/response JSON)
- If library-focused: public functions/classes and their signatures
- If pipeline-focused: input/output formats and validation rules

### G) Quality Bar (must include)
- Logging strategy (levels + what to log)
- Error handling strategy (custom errors if relevant)
- Configuration strategy (env/.env if relevant)
- Testing strategy (unit tests + mocks/fixtures if relevant)
- Minimum 5 test cases listed explicitly

### H) Run Instructions
- Exact commands to run locally (create env, install, run, test)
- Expected outputs (brief)

### I) “Interview Talk Track”
- 60-second explanation
- 3 architecture decisions + trade-offs
- 5 likely interviewer questions + strong answers

### J) Optional Extras (only if truly helpful)
- Nice-to-have improvements that stay aligned with notes

