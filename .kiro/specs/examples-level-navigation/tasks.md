# Implementation Plan: Examples Level Navigation

## Overview

Replace the flat `hubContentLayout` in the Examples tab with a level-based navigation system. Three animated `LevelBadge` widgets filter curriculum cards by difficulty level (Beginner, Intermediate, Advanced) inside a `QScrollArea`. All changes are in `main.py` and `src/modules/translations.py` — no `.ui` file modifications.

## Tasks

- [x] 1. Add translation keys for level names
  - Add `LVL_BEGINNER`, `LVL_INTERMEDIATE`, `LVL_ADVANCED` keys to both `en` and `vi` dictionaries in `src/modules/translations.py`
  - English values: "Beginner", "Intermediate", "Advanced"
  - Vietnamese values: "Cơ bản", "Trung bình", "Nâng cao"
  - _Requirements: 6.1, 6.2_

- [x] 2. Create the LevelBadge widget class
  - [x] 2.1 Define `LevelBadge(QWidget)` class in `main.py` above the `CurriculumCard` class
    - Add `level_clicked = pyqtSignal(str)` signal
    - Constructor accepts `level_key: str`, `color: str`, `icon: str`, `parent=None`
    - Store internal state: `_active`, `_level_key`, `_color`, `_icon`, `_count`, `_is_small`
    - Set fixed width (90px standard, 72px small) and initial `maximumHeight` to inactive height (24px standard, 19px small)
    - Create `QPropertyAnimation` on `maximumHeight` with 200ms duration and `QEasingCurve.InOutCubic`
    - Create internal `QVBoxLayout` with icon label, name label, and count label
    - Apply inactive stylesheet with semi-transparent background and full border-radius (half-circle)
    - Override `mousePressEvent` to emit `level_clicked` signal with `_level_key`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

  - [x] 2.2 Implement `set_active(active: bool)` method
    - If `active` matches current `_active` state, return early
    - Update `_active` flag
    - Stop any running animation, set start/end values for `maximumHeight` animation
    - Active: animate to `active_h` (56px standard, 45px small), apply vibrant stylesheet, show text/icon
    - Inactive: animate to `inactive_h` (24px standard, 19px small), apply muted stylesheet, hide text
    - Start animation
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 2.3 Implement `set_count(count: int)`, `update_resolution(is_small: bool)`, and `retranslate(strings: dict)` methods
    - `set_count`: update `_count` and count label text
    - `update_resolution`: stop animation, update `_is_small`, recalculate fixed width and target heights, reapply stylesheet
    - `retranslate`: update name label text from `strings` dict using the appropriate translation key (`LVL_BEGINNER`, etc.)
    - _Requirements: 2.5, 5.1, 5.2, 6.3_

  - [ ]* 2.4 Write property test for LevelBadge active/inactive height animation targets
    - **Property 1: Level filter visibility invariant** (adapted for badge state)
    - Verify that for any `is_small` flag and any `active` flag, the animation end value equals `active_h` when active and `inactive_h` when inactive
    - **Validates: Requirements 3.1, 3.3**

- [x] 3. Implement `_setup_level_navigation()` in MainWindow
  - [x] 3.1 Create `_setup_level_navigation(self)` method in `MainWindow.__init__` area
    - Get `pageExamples` widget (page 0 of `hubStackedWidget`)
    - Remove existing `hubContentLayout` contents
    - Create new `QVBoxLayout` on `pageExamples` containing:
      - A `QHBoxLayout` (Level_Navigation_Bar) with stretch spacers and three `LevelBadge` instances (Beginner/#3b82f6/⭐, Intermediate/#22c55e/🚀, Advanced/#f97316/🏆)
      - A `QScrollArea` with `widgetResizable=True`, `horizontalScrollBarPolicy=Qt.ScrollBarAlwaysOff`, `frameShape=QFrame.NoFrame`
      - Inside the scroll area: a `QWidget` with a `QVBoxLayout` (`_cards_layout`) for curriculum cards
    - Store references: `self._level_badges` dict, `self._active_level = "Beginner"`, `self._examples_scroll`, `self._cards_layout`, `self._curriculum_cards` list
    - Connect each badge's `level_clicked` signal to `self._on_level_selected`
    - Set Beginner badge as active by default
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 4.1, 4.3, 4.4_

  - [x] 3.2 Call `_setup_level_navigation()` from `__init__` after `hubContentLayout` is found
    - Replace the existing `self.populate_curriculum_hub()` call location so that `_setup_level_navigation()` runs first, then `populate_curriculum_hub()` populates the new `_cards_layout`
    - _Requirements: 1.1, 2.1_

- [x] 4. Checkpoint — Verify level navigation bar renders
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Refactor `populate_curriculum_hub()` for level-based grouping
  - [x] 5.1 Modify `populate_curriculum_hub()` to use `_cards_layout` instead of `hubContentLayout`
    - Clear existing cards from `self._cards_layout`
    - Scan curriculum directory, parse metadata with `_parse_lesson_metadata()`
    - Create `CurriculumCard` for each file, store as `(level, card)` tuples in `self._curriculum_cards`
    - Add all cards to `self._cards_layout`
    - Add a vertical stretch spacer at the end
    - Update each badge count via `set_count()` using grouped counts
    - Call `_apply_level_filter()` at the end
    - _Requirements: 2.3, 2.4, 2.5, 7.1, 7.2_

  - [x] 5.2 Implement `_on_level_selected(level: str)` and `_apply_level_filter()` methods
    - `_on_level_selected`: if level equals `_active_level` return early; update `_active_level`; call `set_active(True/False)` on each badge; call `_apply_level_filter()`; scroll to top
    - `_apply_level_filter`: iterate `self._curriculum_cards`, call `card.setVisible(level == self._active_level)` for each `(level, card)` tuple
    - _Requirements: 2.2, 2.3, 2.4, 3.4_

  - [ ]* 5.3 Write property test for level filter visibility invariant
    - **Property 1: Level filter visibility invariant**
    - Generate random lists of `(level, card_mock)` tuples with levels from {"Beginner", "Intermediate", "Advanced"}, apply `_apply_level_filter()` for a randomly chosen active level, assert visible cards match exactly
    - **Validates: Requirements 2.3, 2.4**

  - [ ]* 5.4 Write property test for badge count matches group size
    - **Property 2: Badge count matches group size**
    - Generate random curriculum metadata dicts with random LEVEL values from the 3 valid levels, group them, verify `set_count()` values match `len(group)`
    - **Validates: Requirements 2.5**

- [x] 6. Checkpoint — Verify level filtering works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Integrate with resolution and translation systems
  - [x] 7.1 Update `refresh_ui_resolution()` to call `update_resolution(is_small)` on each `LevelBadge`
    - Add a block after existing hub content refresh: iterate `self._level_badges.values()` and call `badge.update_resolution(is_small)`
    - Guard with `hasattr(self, '_level_badges')`
    - _Requirements: 5.1, 5.2, 5.4_

  - [x] 7.2 Update `retranslate_ui()` to call `retranslate(strings)` on each `LevelBadge` and re-populate cards
    - Add a block: iterate `self._level_badges.values()` and call `badge.retranslate(strings)`
    - Call `self.populate_curriculum_hub()` to refresh card titles/descriptions in the new language
    - Guard with `hasattr(self, '_level_badges')`
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ]* 7.3 Write property test for localized card text matches metadata
    - **Property 3: Localized card text matches metadata**
    - Generate random metadata dicts with TITLE, TITLE_VI, DESC, DESC_VI fields, select a random language, verify the card displays the correct field
    - **Validates: Requirements 6.4**

- [x] 8. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- All code changes are in `main.py` and `src/modules/translations.py` — no `.ui` file modifications needed
- The `LevelBadge` class should be defined above `CurriculumCard` in `main.py` since it has no dependency on it
