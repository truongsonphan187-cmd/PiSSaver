# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## PROJECT: CIRCULAR LED MATRIX SCREENSAVER (PiSSaver)

---

| **Field** | **Details** |
| :--- | :--- |
| **Project** | PiSSaver (Circular LED Matrix Screensaver) |
| **Role** | Senior Product Manager & Tech Lead |
| **Stakeholder** | The Boss |
| **Status** | Implementation Complete & Released |
| **Version** | v1.3 (Majestic Ocean Swell & Robust Triple-Layer Dismissal) |
| **Last Updated** | 2026-11-11 |

---

## 1. PRODUCT VISION & OBJECTIVES

**PiSSaver** is a high-performance Windows screensaver that reimagines custom artwork as an illuminated circular LED matrix display:
1. **Zero Resource Idle Footprint:** Resides quietly in the Windows System Tray with **0.0% CPU usage** and < 30MB RAM.
2. **Instant On-Demand Fullscreen:** Left-clicking the tray icon immediately spawns borderless fullscreen windows covering **all active monitors**.
3. **Power Keep-Awake:** Calls Win32 API `SetThreadExecutionState` to prevent OS display sleep and system idle sleep during playback.
4. **Smart Adaptive Crop/Fit Engine:**
   * Automatically fills displays when aspect ratios are close (e.g. 16:9 on 16:10 or 16:10 on 16:9) with **zero black bars**.
   * Preserves exact proportions (Aspect Fit) for square 1:1 artwork (such as Michael Jackson's *Invincible* album) or 4:3 images without awkward cropping, padding outer margins with an unlit LED dot matrix.
5. **Majestic Ocean Swell (3x Wavelength):**
   * Uses a wide wavelength ($\lambda = 255.0$ LED dots) to simulate an expansive, rolling ocean tide sweeping across the screen.
   * Maps wave elevation directly to bulb brightness: Crests reach `115%` brightness; troughs deepen to `~42%` for tangible 3D wave depth while preserving authentic diode colors.
6. **Triple-Layer Dismissal Architecture:**
   * Direct widget event forwarding + Global Qt application event filter + 50ms Win32 cursor displacement polling.
   * Ensures moving the mouse firmly or pressing any key exits the screensaver 100% reliably.

---

## 2. FUNCTIONAL SPECIFICATIONS

### 2.1 Background Tray Mode
* Application starts without creating a taskbar entry.
* A single-instance mutex (`Global\\PiSSaver_SingleInstance_UniqueMutex_2026`) prevents duplicate tray processes.
* No rendering loops or timers execute while idle in the tray.

### 2.2 System Tray Context Menu
Right-clicking the tray icon exposes:
* **🚀 Start Screensaver:** Trigger fullscreen mode immediately.
* **🖼️ Choose Image...:** File dialog to select image files (`.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`).
* **⚙️ LED Dot Size:** Fine (6px), Medium (10px - default), Coarse (16px).
* **🌊 Wave Speed:** Static (0.0), Slow & Chill (0.8), Standard (1.2), Fast (2.0).
* **📁 Open Image Folder:** Opens the directory containing `custom.jpg`.
* **🔄 Run on Windows Startup:** Registers executable path into `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.
* **❌ Exit:** Tears down resources and closes the application cleanly.

### 2.3 Visual Pipeline & Shader Specifications
* **Circular LED Masking:**
  * Grid pitch: $S$ pixels.
  * Dot radius: $R = 0.42 \times S$.
  * Smoothstep edge anti-aliasing in interval $[R - 0.75, R + 0.25]$.
  * Convex dome lens gradient and specular glint on top-left of each diode.
* **Wave Equation:**
  $$\theta = \left(\frac{x_{\text{cell}} + y_{\text{cell}}}{\lambda}\right) \times 2\pi - (t \times \text{speed} \times 1.5)$$
  $$s = \sin(\theta)$$
  $$\text{Luminosity} = \begin{cases} 
  \text{mix}(1.0, 1.15, \text{smoothstep}(0.0, 1.0, s)) & \text{if } s \ge 0 \\
  \text{mix}(1.0, 0.42, \text{smoothstep}(0.0, -1.0, s)) & \text{if } s < 0 
  \end{cases}$$

---

## 3. INPUT DISMISSAL ARCHITECTURE (BUGFIX & VERIFICATION)

To prevent unresponsiveness when shaking the mouse:
1. **Child Widget Routing:** `LEDMatrixWidget` (QOpenGLWidget) enables mouse tracking and explicitly forwards `mouseMoveEvent`, `mousePressEvent`, `keyPressEvent`, and `wheelEvent` to `ScreensaverWindow`.
2. **Global Event Filter:** `GlobalScreensaverFilter` installed on `QApplication.instance()` intercepts user input events application-wide.
3. **Cursor Polling Watchdog:** A dedicated 50ms polling timer monitors `QCursor.pos()`. If displacement $\Delta > 15\text{px}$ after a 300ms initial launch grace period, the screensaver terminates immediately.
