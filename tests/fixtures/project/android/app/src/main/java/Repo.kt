package com.example

//region Networking
/**
 * Fetches a user.
 * @param userId the user id
 * @return the user
 */
suspend fun fetch(userId: String): User = api.user(userId) // call api
/* outer /* inner */ still comment
   end */
val x = 1 /* a /* b */ c */ + 2
//noinspection SpellCheckingInspection
// ktlint-disable max-line-length
// @formatter:off
val s = """raw // not comment"""
//endregion
