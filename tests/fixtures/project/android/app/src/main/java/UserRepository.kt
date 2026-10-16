interface UserRepository {
    suspend fun user(id: String): User
    // suspend fun users(): List<User>
}

class Impl {
    fun run() {
        // val x = compute()
    }
}
