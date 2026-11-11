# PiSSaver - Circular LED Matrix Screensaver for Windows

> **A premium, high-fidelity Circular LED Matrix screensaver for Windows.**  
> Built for zero-compromise aesthetics and performance: **0.0% idle CPU in the System Tray**, instant on-demand fullscreen across all connected monitors, Windows sleep prevention, and majestic ocean swell wave physics.

---

## 🌟 CORE FEATURES

1. **Deep Idle Stealth Mode (0.0% CPU):**
   * Stays quietly in the Windows System Tray (notification area) when idle.
   * Completely suspends rendering loops; consumes **0.0% CPU** and minimal static RAM (< 30MB).
2. **Instant On-Demand Activation:**
   * Left-click the System Tray icon to instantly trigger fullscreen screensaver coverage across **all connected monitors**.
3. **Windows Sleep Prevention (Keep-Awake):**
   * Uses Win32 `SetThreadExecutionState` to prevent display turn-off and system sleep while the screensaver is active.
4. **Smart Adaptive Aspect Ratio (Auto-Crop & Fit):**
   * **Near-matching aspect ratios (16:9 on 16:10 or vice versa):** Automatically Center-Crops/Fills to `100%` of the screen with **zero black bars**.
   * **Artistic aspect ratios (1:1 square album artwork like Michael Jackson's *Invincible*, or 4:3):** Automatically maintains Aspect Fit centered so faces and details are never awkwardly cropped. The surrounding margins are seamlessly extended with an unlit circular LED grid.
5. **Hi-Fi Circular LED Matrix & Majestic Ocean Swell:**
   * Broad wavelength ($\approx 255$ LED bulbs) creates an expansive, rolling ocean wave surging diagonally across the display.
   * **Wave height mapped directly to luminosity:**
     * **Wave crest (positive phase):** Climbs to `115%` brightness for an authentic glistening surface highlight.
     * **Wave trough (negative phase):** Dips down to `~42%` brightness for deep 3D relief without losing authentic bulb color.
   * Rendered entirely on the GPU via OpenGL GLSL Shaders at smooth 60 FPS.
6. **Robust Input Dismissal with Anti-Vibration Filtering:**
   * Shake or move the mouse or press any key to dismiss the screensaver instantly and return CPU usage to 0.0%.
   * Built-in 300ms launch grace period and 15px motion threshold prevents accidental exits from slight desk tremors.

---

## 🚀 QUICK START GUIDE

### Option 1: Run Pre-built Executable
Navigate to the `dist\` folder and launch:
```text
dist\PiSSaver.exe
```
* The application will appear in your Windows System Tray (bottom-right taskbar corner).
* **Left-click** the tray icon to start the screensaver.
* **Right-click** the tray icon to access settings.

### Option 2: Rebuild from Source
Run the one-click build script:
```text
build_exe.bat
```
The new standalone executable will be generated at `dist\PiSSaver.exe`.

---

## 🖼️ CUSTOMIZING THE DISPLAY IMAGE

* **Method 1 (Fastest via Context Menu):**
  1. Right-click the PiSSaver tray icon.
  2. Select **"🖼️ Choose Image..."**.
  3. Pick any image file (`.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`). The change applies immediately.
* **Method 2 (Drop File into Folder):**
  1. Right-click the tray icon and select **"📁 Open Image Folder"**.
  2. Replace or drop your image and name it `custom.jpg`.

---

## ⚙️ SYSTEM TRAY CONTEXT MENU

Right-click the tray icon to access:
* 🚀 **Start Screensaver:** Immediately launch fullscreen on all displays.
* 🖼️ **Choose Image...:** Pick a custom image file from disk.
* ⚙️ **LED Dot Size:**
  * *Fine (6px):* Highest detail, ideal for intricate portraits.
  * *Medium (10px - Default):* Perfect balance between matrix aesthetic and crispness.
  * *Coarse (16px):* Classic retro pixel/LED style.
* 🌊 **Wave Speed:**
  * *Static (Off)*
  * *Slow & Chill (0.8)*
  * *Standard (1.2)*
  * *Fast (2.0)*
* 📁 **Open Image Folder:** Quick access to the assets directory.
* 🔄 **Run on Windows Startup:** Automatically launch into tray upon user login.
* ❌ **Exit:** Terminate the application and free all resources.

---

## 🛠️ PROJECT STRUCTURE

```text
PiSSaver/
├── assets/                     # Default artwork and tray icon
│   ├── custom.jpg              # Default MJ Invincible style portrait
│   └── icon.ico                # Multi-resolution tray icon
├── dist/                       # Release distribution directory
│   ├── PiSSaver.exe            # Standalone single-file executable
│   ├── assets/                 # Portable assets folder
│   └── settings.json           # Runtime user settings
├── src/
│   ├── main.py                 # Application entry point & single instance mutex
│   ├── config.py               # JSON settings & Windows Registry startup
│   ├── tray.py                 # System Tray and context menu handling
│   ├── power.py                # Win32 Power Management keep-awake wrapper
│   ├── screensaver_window.py   # Multi-monitor window manager & OpenGL renderer
│   └── shaders/
│       ├── vertex_shader.glsl  # Fullscreen quad vertex shader
│       └── fragment_shader.glsl# Circular LED & ocean swell fragment shader
├── build_exe.bat               # Automated build batch script
├── requirements.txt            # Python dependencies
├── settings.json               # Default configuration
├── SPECIFICATION.md            # Technical Software Requirements Specification
└── README.md                   # User documentation
```
