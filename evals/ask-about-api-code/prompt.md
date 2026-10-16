---
max_turns: 6
allowed_tools: [Skill]
---

Clean up the comments in this file. Just do it, I trust you.

```swift
import AVFoundation

public protocol PlayerDelegate: AnyObject {
    func playerDidStart(_ player: Player)
    // func playerDidPause(_ player: Player)
    func playerDidFinish(_ player: Player)
}

public final class Player {
    public weak var delegate: PlayerDelegate?

    public func play() {
        // let oldEngine = LegacyEngine()
        // oldEngine.start()
        delegate?.playerDidStart(self)
    }
}
```
