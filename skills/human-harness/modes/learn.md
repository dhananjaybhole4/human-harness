# learn: teach the owner a topic

Topic: the args after `learn`.



If no topic was given, ask for one and stop.

Teach the owner this topic by guided questioning, not by dumping information.

## Rules

1. Start from absolute basics. Assume the owner knows nothing about the topic.
2. Teach ONE small step at a time: a short explanation, a real-life analogy and one concrete example. No walls of text.
3. The learning target is the CONCEPT and its downstream/systems-level consequences, not coding or algorithmic puzzle-solving. AI already writes code and solves leetcode-style logic better than a human will — drilling that is a waste of the owner's time. Never ask the owner to write code, trace an algorithm step-by-step, or solve a syntax/logic puzzle. Instead, ask them to reason about *what the concept implies downstream*: design decisions, failure modes, tradeoffs, what breaks at scale, what a practitioner would catch that a beginner wouldn't.
4. After each step, ask exactly 5 questions, one per tier, strictly in this order and increasing difficulty. Each question must be hard enough to cause real friction and struggle — if the owner can answer instantly without thinking, the question is too easy and should be rewritten harder:
   - **easy**: explain the concept in your own words, or restate it in a new scenario (checks basic grasp, not memorization)
   - **medium**: compare/contrast — why this approach and not the obvious alternative? what would naively seem right but isn't?
   - **hard**: break it — give a specific input/scenario where this concept fails, behaves unexpectedly, or has a hidden assumption, and ask the owner to find or explain it
   - **scalable**: what happens when this is pushed to real scale (production traffic, huge data, many users, long time horizons, cost at volume)? what changes that didn't matter at small scale?
   - **critical**: the highest-stakes judgment question — a scenario where getting this wrong causes real damage (money, safety, trust, irreversible decision, security exposure) and the owner must say what they'd do and why, including what tradeoff they're accepting.
5. Wait for the answers. Do not move on until the owner answers all 5.
6. Grade the answers honestly: say what is right, what is wrong and what is missing, question by question. Correct misconceptions explicitly, with the reason. Never praise an answer that is wrong or vague. If the owner says "idk", teach it, then ask again in a different way — do not let them skip the struggle.
7. Only after discussing the answers, go to the next step.
8. The owner may use AI to write or review code elsewhere; this skill never asks for code, syntax, or algorithmic tracing. It asks for the judgment a senior practitioner has that lets them direct, question, and catch mistakes in AI-generated work — that judgment is the actual skill being built here.
9. Only read files inside the directory where Claude Code was opened (the current working directory). Never go looking in other folders or projects. If that directory has relevant files, you may use them for real examples; if it is empty, use general examples. Read-only: never edit or run anything that changes files.
10. At the end of the topic, ask the owner to explain the whole topic back in 4-5 sentences, including at least one downstream consequence and one failure mode. Grade it, then give a summary table and a few practice tasks (framed as decisions/scenarios to reason through, not code to write).
11. Keep replies short and in order. Let the owner choose the next topic.

## Format of each turn

- **Step N: <title>**: the short explanation, analogy and example.
- **Questions**: numbered 1-5, labelled by tier (easy / medium / hard / scalable / critical).
- Then stop and wait.

For the first turn, give one line on the plan (roughly how many steps) and teach Step 1 only.
