# 🎨 Design Specification: KDI Story Mode

## 1. The KDI Hub (Column 1)
*   **Theme**: Deep Navy background with Gold borders and text highlights.
*   **The Tutor**: A persistent "KDI Instructor" bubble at the top of the column.
*   **Instruction Card**: Uses a "Gold Frosted" border to indicate it is an active mission.

---

## 2. The KDI Robot (Mascot: The Hatchling)
*   **Final Design**: Based on **V1.1 (Refined)**.
*   **Visual**: A navy blue robot core peeking out from a gold egg-shell logo.
*   **Branding**: "KDI" text visible on the top-left shell piece.
*   **Animations**: 
    *   `Victory`: Robot does a 360 spin with gold particles.
    *   `Error`: Robot's eyes turn red and it shakes its head.
    *   `Thinking`: A gold light pulses on its head.

---

## 3. The "Smart Canvas" Overlay
*   **Container**: `QStackedWidget` in the results area (Right Column).
*   **Transition Effect**: A "Slide" or "Fade" transition when moving from the Virtual Animation to the Live Camera.
*   **Overlap HUD**: When the camera is active, a small Gold "HUD" overlay shows the Robot's current "Brain State" (detections, variables).

---

## 4. The Graded Footer (HUD)
*   **Placement**: Bottom of the editor or top of the variables column.
*   **Design**: 5 Glowing Hearts (Navy fill with Gold glow).
*   **Sound (Optional)**: A subtle "Ding" for success and a "Buzzer" for heart loss.
