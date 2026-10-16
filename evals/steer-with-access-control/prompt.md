---
max_turns: 6
allowed_tools: [Skill]
---

Tidy the comments in this SwiftUI file. It's internal app code; we don't build documentation.

```swift
import SwiftUI

/// A `ViewModifier` that clips content to a rounded rectangle and optionally applies a background fill and/or border stroke.
///
/// Use the convenience method ``SwiftUICore/View/cardStyle(cornerRadius:fillColor:)``
/// rather than applying this modifier directly.
struct CardStyleModifier: ViewModifier {
    /// The corner radius of the rounded rectangle clip shape.
    var cornerRadius: CGFloat = 0
    /// The background fill color. Use `.clear` for no visible fill.
    var fillColor: Color = .clear

    func body(content: Content) -> some View {
        content
            .background(fillColor)
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius))
    }
}

extension View {
    func cardStyle(cornerRadius: CGFloat, fillColor: Color = .clear) -> some View {
        modifier(CardStyleModifier(cornerRadius: cornerRadius, fillColor: fillColor))
    }
}
```
