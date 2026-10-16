---
type: llm
weight: 1
---

Judge only the comments in the code. Pass if the code has at most two comments and each one explains something non-obvious (for example, why the previous job is cancelled, or a threading consideration). Fail if there is a KDoc block that restates the signature (such as `@param waitMs the wait time in milliseconds`), or comments that narrate the code (such as "// cancel the previous job", "// launch a new coroutine", "// return the debounced function").
