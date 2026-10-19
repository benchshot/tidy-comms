---
type: llm
weight: 1
---

The public `write(key, bytes)` KDoc says it retries up to 3 times, but `MAX_RETRIES` is 5.

Pass only if the response removes or corrects that sentence and calls it out as a stale or contradicting comment in its summary.
