---
max_turns: 6
allowed_tools: [Skill]
---

This is from our Android app (not a library, and we don't publish docs). Tidy the comments and return the full file.

```kotlin
package com.example.app.profile

// ktlint-disable max-line-length

//region Profile loading
/**
 * Loads the profile.
 *
 * @param userId the user id
 * @return the profile
 */
suspend fun loadProfile(userId: String): Profile {
    // get the repository
    val repo = ProfileRepository.instance
    // The backend returns 404 for deactivated users instead of an empty profile,
    // so treat that as "no profile" rather than an error.
    return repo.fetch(userId) ?: Profile.EMPTY
}
//endregion
```
