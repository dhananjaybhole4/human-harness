<div align="center">

# 🧭 human-harness

**Keep the human in charge of the AI that writes their code.**

A [Claude Code](https://docs.claude.com/en/docs/claude-code) skill that interviews you until it knows exactly what you want,
writes it down as a spec, rules and checks, and then holds the AI to them, including on hidden test cases the AI can never see.

*You judge the work by how it behaves, without reading the code.*

[Install](#-install-30-seconds) · [How it works](#-how-it-works) · [Commands](#-commands) · [Learn mode](#-learn-mode) · [FAQ](#-faq)

</div>

---

## 😩 The problem

You ask an AI agent to build something. It says "done ✅". Then:

- it built **something close to** what you meant, not what you meant
- it **quietly changed the test** so the test would pass
- it touched the folder you told it to stay out of
- next session it has **forgotten** every decision you made together
- you can't tell if it's right, because you'd have to read 2,000 lines of code

Most agent setups put rules on the **AI**. human-harness gets **what's in your head** onto paper first, then makes the AI prove its work against it.

## ✨ What you get

| | |
|---|---|
| 🎤 **Deep interview** | Goal, real samples, numeric "done" criteria, never-touch list, risks. It keeps asking until there are no adjectives left, only numbers and examples. Nothing is ever asked twice. |
| 📜 **A harness in your repo** | `SPEC.md`, `BOUNDARIES.md`, `checks.toml`, `STATUS.md`, `DECISIONS.md`, `ARCHITECTURE.md`. Short, plain language, owned by you. |
| ✅ **`harness/verify`** | One command, a PASS/FAIL table. Your acceptance checks, plus built-in checks for code size, hardcoded test values and doc size. |
| 🔒 **Hidden exam (holdout)** | You seal test cases in an encrypted vault outside the repo. The AI is **blocked** from reading them, so it can't overfit. You run the exam and see only the score. |
| 🛡️ **Guard hooks** | The AI can't silently edit your approved spec, rules or checks: you get a prompt. Fingerprints catch any change made behind your back. |
| 🧠 **Memory across sessions** | Every session starts with the rules and current status loaded. The AI can't finish a session without updating the status. |
| 🌿 **Branch-aware** | Each git branch gets its own mini-spec. `merge` compares branch and main side by side, then keeps it or drops it (and keeps the lesson). |
| 🔁 **Postmortems** | Something went wrong? It becomes a permanent rule or check, so the same mistake can't come back. |
| 🎓 **Coaching + learn mode** | It points out the engineering skill you're weakest at while you work, and teaches any topic with hard questions on request. |

## 🎓 The exam analogy

| School | human-harness |
|---|---|
| The syllabus | `SPEC.md`: what "done" means, in numbers |
| School rules | `BOUNDARIES.md`: never / ask first / free |
| Practice questions | `harness/verify`: the AI runs these as often as it likes |
| The sealed final exam | `verify --holdout`: only **you** run it, the AI never sees the questions |
| The teacher signs the rulebook | `verify --lock`: fingerprints what you approved |

An AI that only passes the practice questions has memorised them. Passing the sealed exam shows it actually works.

## 🚀 Install (30 seconds)

```bash
git clone https://github.com/dhananjaybhole4/human-harness.git
cd human-harness && ./install.sh
```

Restart Claude Code, open any project and type:

```
/human-harness
```

**Needs:** Python 3.11+, git, and openssl (only for the hidden exam). `install.sh` copies the skill to
`~/.claude/skills/human-harness`, backs up `~/.claude/settings.json`, and adds 3 hooks to it. It is safe to re-run.

## 🔧 How it works

```
 you ──▶ /human-harness init ──▶ interview ──▶ harness/ (spec, rules, checks)   ◀── you approve
                                                     │
          /human-harness run ──▶ AI builds ──▶ harness/verify ──▶ PASS? ──▶ stops for your decisions
                                                     │
            you, in your own terminal ──▶ verify --holdout ──▶ score on cases the AI never saw
```

1. **`init`**: the interview, in 7 areas: purpose → context → inputs/outputs → success → boundaries → risks → approach. No code is written during init.
2. **You approve.** Spec, rules and checks only change with your yes. Then `verify --lock`.
3. **`run`**: the AI builds in a loop, proves each step with `verify`, and stops when it needs you (milestone done, a question only you can answer, the same check failing 3 times).
4. **`verify --holdout`**: the real test, run by you.
5. **`update` / `postmortem`**: when plans change or something breaks, the harness learns.

## 📋 Commands

| You type | Where | What it does |
|---|---|---|
| `/human-harness init` | Claude Code | Interview → harness (on a branch: a short branch interview) |
| `/human-harness run` | Claude Code | Build until done or until it needs you (`/loop /human-harness run` for unattended) |
| `/human-harness update [add X]` | Claude Code | Short re-interview, or add new scope |
| `/human-harness check` | Claude Code | Health report: GREEN / AMBER / RED |
| `/human-harness merge` | Claude Code | Finish a branch: compare with main, keep or drop |
| `/human-harness postmortem` | Claude Code | Turn a mistake into a permanent fix |
| `/human-harness learn <topic>` | Claude Code | Learn any topic, step by step |
| `harness/verify` | terminal | Practice test: PASS / FAIL |
| `harness/verify --compare [ref]` | terminal | This branch vs main, side by side |
| `harness/verify --seal` | **your** terminal only | Encrypt hidden exam cases |
| `harness/verify --lock` | **your** terminal only | Sign the approved rules and checks |
| `harness/verify --holdout` | **your** terminal only | Run the hidden exam, scores only |

## 🎓 Learn mode

```
/human-harness learn vector databases
```

You get one small step at a time, each with an analogy and an example, then **5 questions** that get harder:
**easy → medium → hard → scalable → critical**. The answers are graded honestly: wrong or vague answers don't get praise, and "idk" gets taught and asked again in a different way.

It never asks you to write code. With AI writing the code, the skill that matters is the judgment to **direct it and catch its mistakes**: trade-offs, failure modes, what breaks at scale. That's what learn mode trains.

## 📁 What it adds to your project

```
harness/
├── SPEC.md          # goal, examples, "done when" table (≤ ~60 lines)
├── BOUNDARIES.md    # never / ask first / free (≤ 15 rules)
├── checks.toml      # acceptance checks (approved by you)
├── checks/          # check scripts
├── STATUS.md        # done / next / needs you / not verified (≤ 30 lines)
├── DECISIONS.md     # date — decision — why, one line each
├── ARCHITECTURE.md  # map of the code, for the AI
├── INTERVIEW.md     # every Q&A, so nothing is asked twice
├── branches/<name>/ # per-branch spec and status
└── verify           # the PASS/FAIL command
```

The hidden exam lives **outside** the repo, in `~/harness-holdouts/`, encrypted.

## ❓ FAQ

**Is the holdout actually hidden from the AI?**
The guard hook blocks any tool call that mentions the vault or the owner-only flags, and the cases are encrypted with a password only you know. It's a strong guard rail, not a sandbox.

**Do I need to be a programmer?**
No. It was built for people who judge work by results. Everything you approve is plain language with numbers and examples.

**Does it work on an existing project?**
Yes. `init` reads the repo first and asks you about the decisions it finds (intentional, legacy or unknown?).

**ML projects?**
There's an ML add-on: a mandatory baseline to beat, data-leakage checks (split overlap, future features), and a shuffled-label sanity test.

**Uninstall?**
Delete `~/.claude/skills/human-harness` and remove its 3 hooks from `~/.claude/settings.json`. A backup of that file was made when you installed.

## 🤝 Contributing

Issues and PRs are welcome, especially new **domain add-ons** (`skills/human-harness/addons/`): web apps, data pipelines, embedded, mobile.
If the harness saved you from a bad AI "done ✅", open an issue and tell the story.

## ⭐ If it helps you

Star the repo so others can find it.

## License

[MIT](LICENSE)
