# 🎨 Design Specification: Lessons & Expandable Examples Overhaul

## 1. UI/UX Architecture (The Hybrid Learning Hub)
The first tab of the Hub is designated primarily for interactive **Gamified Lessons**. Legacy examples remain accessible via a dynamic collapsible footer.

---

## 2. Dynamic Collapsible "Examples" Implementation
*   **Component**: Instead of an unyielding `QSplitter`, a custom **Collapsible Examples Panel** will be placed at the bottom.
*   **Expansion Logic**:
    *   *Default State*: Collapsed (height ~40px showing only a "🎯 Curriculum Examples" header with a chevron ▽).
    *   *Expanded State*: Animates height upwards smoothly or sets the `QSplitter` sizes to `[400, 600]`.
*   **Behavior**: Fits ergonomically within the current dynamic layout routines.

---

## 3. Challenge Scoring Flow
*   Execution evaluation mappings.
