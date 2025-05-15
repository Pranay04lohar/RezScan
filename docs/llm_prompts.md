# ⚡ Vibe Coding Prompts Cheat Sheet (for Cursor or any LLM IDE)

Use this file to copy-paste or customize prompts inside Cursor to guide AI assistance smartly as you build full-fledged systems.

---

## 🧪 Rapid Prototyping → Clean Rewrite

```txt
I’ve iterated several times to get this working. Here's the current file structure and final code. Now, please help me rewrite it from scratch, clean and minimal, as if building from zero—but using what we've learned.
```

---

## 📚 Doc Grounding / BYOD (Bring Your Own Docs)

```txt
Use only the information in `docs/supabase_auth_api.md` to implement user signup and login flow. Ignore all other assumptions. Build the auth module cleanly from that doc alone.
```

---

## 🎭 Role-Based Prompting

```txt
Act as a senior backend engineer. Given this file structure and current implementation, how would you architect the service layer for scalability?

You're a performance optimization expert. Here’s my component—it’s slow. Tell me exactly what to fix and how.
```

---

## 🧠 Thought-Dumping (Context Feeding)

```txt
Here’s my folder structure, relevant code snippets, and what I’m trying to achieve. Something’s not working, and I’m stuck. Based on this complete context, what should I do next?
```

---

## 🧼 Atomic Commits

```txt
Based on the changes I’ve made in this commit, write a meaningful commit message that describes the single responsibility it touches.
```

---

## 🔁 Reversible Refactors (Sandboxing)

```txt
I’m creating a new branch to test this refactor. Help me isolate the current logic into a separate file/module so I can experiment without breaking the main workflow.
```

---

## 🎨 Visual Planning

```txt
Create a Mermaid.js sequence diagram or flowchart of how data moves between frontend, backend, and database in this project. Use the current file structure as reference.
```

---

## 🧾 Prompt Logging / Chat Journal

```txt
Write a short summary of this prompt-response exchange and store it in `ai_history.md` with today’s date. I want to track what worked, what failed, and key insights.
```

---

## 🗃️ Modular Mindset

```txt
Refactor this code into services and modules. Split logic into `authService`, `dbService`, and `emailService`. Keep each module loosely coupled and testable.
```

---

## ⛓️ Dry Run Everything

```txt
Help me dry run this function line by line with sample inputs. Show me what each variable looks like at every step, and point out any logic bugs.
```

---

✅ Tip: Keep this file updated with any powerful custom prompts you develop.

> Live by the vibe. Ship by the system. 🚀
