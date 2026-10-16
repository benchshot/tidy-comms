//
//  Sample.swift
//  Copyright (c) 2026 Example. All rights reserved.
//

import Foundation

// MARK: - Fetching

/// Fetches the user.
func fetchUser(id: String) -> String {
    // Build the URL
    let url = "https://example.com/users/\(id)" // trailing note
    let s = "not // a comment"
    /* block
       comment */
    let multi = """
    // inside a string
    """
    // let old = legacy()
    return url + s + multi /* inline */
}
