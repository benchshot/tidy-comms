---
max_turns: 6
allowed_tools: [Skill]
---

Write a Kotlin function `fun debounce(waitMs: Long, scope: CoroutineScope, action: (String) -> Unit): (String) -> Unit` that returns a debounced version of `action`: each call cancels the previously scheduled one and schedules `action` to run after `waitMs`. Just give me the code.
