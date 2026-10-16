---
type: llm
weight: 1
---

Judge the code the response returns. The code was pasted, so no file on disk needs editing.

Pass only if all of these hold in the returned file:
- The KDoc block (`Loads the profile.`, `@param userId the user id`, `@return the profile`) is removed entirely, not shortened.
- `// get the repository` is removed.
- `// ktlint-disable max-line-length`, `//region Profile loading` and `//endregion` are all still present, unchanged.
- The comment explaining that the backend returns 404 for deactivated users is kept (it may be tightened, but the reason must survive).
- No code line was changed.
