## The simplest correct workflow (so you don’t make mistakes)

### ✅ Use **separate chats** (recommended)

For each day, create **3 chats**:

1. **D1 Notes**
2. **D1 PoC**
3. **D1 Deploy**
   (Optional: **D1 Debug** only if you hit errors)

Why: keeps context clean, avoids long history drift/hallucinations, faster iterations.

---

## Exactly what to do in each chat

### Chat 1: **D1 Notes**

1. Paste **Preset (once)**
2. Send: `Day 1 – Notes (Step 1 map only)`
3. Then: `Day 1 – Notes – Part 1` (and Part 2, Part 3 if needed)
4. End with: `Day 1 – Quick Revision`

### Chat 2: **D1 PoC**

1. Paste **Preset (once)**
2. Send: `Day 1 – PoC`

### Chat 3: **D1 Deploy**

1. Paste **Preset (once)**
2. Send: `Day 1 – Deployment`

### Optional Chat 4: **D1 Debug**

Only paste logs/errors here.

---

## When to start a new chat (rules)

Start a new chat when:

* switching task type (**notes → code → deploy**)
* the notes chat becomes too long (after ~2–3 parts)
* you start troubleshooting (logs)

---

## Common mistakes to avoid

### ❌ Mistakes

* Pasting **Notes + PoC + Deploy** in one message (leads to huge mixed output)
* Keeping one mega-chat for many days (context overload → drift)
* Asking for deep dive + “strong interview answers” in the *high-level map* step (causes unwanted deep dive)
* Adding new scope mid-day (“also add Terraform, also add UI…”) → goal dilution

### ✅ Do instead

* One chat = one purpose (Notes OR PoC OR Deploy)
* One day = finish the unit before moving on
* Keep Day 1 strictly Day 1 scope

---

## Do / Don’t checklist (keep you on track)

### ✅ DO

* Use chat titles like: `genai-enterprise-labs – D1 Notes / PoC / Deploy`
* Commit daily with a clear message (`feat(d1): ...`)
* End each chat with:

  * “Give me a commit summary + next-step checklist”

### ❌ DON’T

* Don’t paste the full Plan A daily
* Don’t mix tasks in one prompt
* Don’t chase extra topics (DSA, full ML math, etc.) unless required by Plan A

---

## One-line rule to remember

**“One day = one outcome. One chat = one task.”**
