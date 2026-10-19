---
max_turns: 6
allowed_tools: [Skill]
---

Tidy the comments in this file from our app and return the full file. We don't build docs for it.

```kotlin
package com.example.app.cache

class DiskCache(private val dir: File) {

    /**
     * Evicts least-recently-used entries until the total size is at most [maxBytes].
     * Pinned entries are never evicted, so the result can still exceed [maxBytes].
     */
    fun trim(maxBytes: Long) {
        entries.filterNot { it.pinned }
            .sortedBy { it.lastAccess }
            .takeWhile { totalBytes() > maxBytes }
            .forEach { remove(it) }
    }

    /**
     * Restores the index from the last snapshot written by [saveSnapshot], not
     * by rescanning [dir]. We deliberately chose this over a rescan because we
     * think startup speed matters more than anything else here.
     */
    fun restoreIndex() {
        index = Snapshot.read(dir.resolve(SNAPSHOT_FILE)) ?: Index.EMPTY
    }

    /**
     * Writes [bytes] to disk.
     *
     * Retries up to 3 times on IOException.
     */
    fun write(key: String, bytes: ByteArray) {
        write(key, bytes, attempt = 0)
    }

    /**
     * Overload that tracks the attempt count, so retries don't re-enter the
     * public method and double-count the write in metrics.
     */
    private fun write(key: String, bytes: ByteArray, attempt: Int) {
        try {
            dir.resolve(key).writeBytes(bytes)
            metrics.recordWrite()
        } catch (e: IOException) {
            if (attempt < MAX_RETRIES) write(key, bytes, attempt + 1) else throw e
        }
    }

    companion object {
        private const val MAX_RETRIES = 5
        private const val SNAPSHOT_FILE = "index.snapshot"
    }
}
```
