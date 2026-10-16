---
type: llm
weight: 2
---

Judge the code the response returns. The code was pasted, so no file on disk needs editing.

The updated file must completely remove every comment that only restates the code or the names. That means these, with none of them surviving in any form, shortened or reworded:
- "A cache for images."
- "The underlying storage for cached images, keyed by URL string"
- "Returns the image for the given URL." along with its `- Parameter url: The URL.` and `- Returns: The image, if cached.` lines
- "Look up the image in the cache using the URL's absolute string as the key"
- "Store it"

Fail if any of them is still present, or if one was replaced by a shorter version of itself, such as "// Cache storage" or "/// Image lookup".
