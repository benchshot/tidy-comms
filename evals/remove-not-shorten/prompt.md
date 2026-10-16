---
max_turns: 6
allowed_tools: [Skill]
---

Tidy the comments in this file and give me back the full updated file.

```swift
//
//  ImageCache.swift
//  Copyright (c) 2026 Example Inc. All rights reserved.
//

import UIKit

// MARK: - ImageCache

/// A cache for images.
final class ImageCache {
    // The underlying storage for cached images, keyed by URL string
    private let storage = NSCache<NSString, UIImage>()

    /// Returns the image for the given URL.
    /// - Parameter url: The URL.
    /// - Returns: The image, if cached.
    func image(for url: URL) -> UIImage? {
        // Look up the image in the cache using the URL's absolute string as the key
        return storage.object(forKey: url.absoluteString as NSString)
    }

    func insert(_ image: UIImage, for url: URL) {
        // NSCache can evict during a memory warning while we insert; decode first so
        // the cache never holds an image that still has to be decompressed on the main thread.
        let decoded = image.preparingForDisplay() ?? image
        // Store it
        storage.setObject(decoded, forKey: url.absoluteString as NSString)
    }
}
```
