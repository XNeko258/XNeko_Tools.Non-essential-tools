# XNeko_Tools · Non-essential Tools

A companion repository for [XNeko_Tools](https://github.com/XNeko258/XNeko_Tools), used to distribute optional and non-essential tool modules.

These modules are **not required** for the core toolbox to work. They are experimental, fun, or niche add-ons that extend XNeko Tools beyond the standard feature set.

---

## ⚠️ Requirements

**The base toolbox is required.**

Before installing any module from this repository, you must first install [XNeko_Tools](https://github.com/XNeko258/XNeko_Tools).

👉 **Download the base toolbox here:**
[XNeko_Tools](https://github.com/XNeko258/XNeko_Tools/releases)

Modules from this repository will not load without it.

---

## 📦 Available Modules

| Module | Category | Description |
|--------|----------|-------------|
| [Music Player](https://github.com/XNeko258/XNeko_Tools.Non-essential-tools/releases/tag/Blender_Music_Player) | Media Tools | A local audio player inside Blender's N-panel. Supports folder scanning, playlist browsing, shuffle, loop, and jump controls. |
| [UE Format (Improved)](https://github.com/XNeko258/UEFormat-XNeko/releases) | Importers | Blender importer for `.uemodel` / `.ueanim` / `.uepose` files. Rewritten from [h4lfheart/UEFormat](https://github.com/h4lfheart/UEFormat) with performance and safety improvements. Ships as both an XNeko_Tools module and a **standalone plugin** — the standalone version does not require XNeko_Tools. |

More modules will be added over time.

---

## 🛠️ Installation

1. Make sure [XNeko_Tools](https://github.com/XNeko258/XNeko_Tools) is installed and working in your Blender.
2. Download the module folder you want (e.g. `music_player/`).
3. Place it inside the base toolbox's tool directory:
     XNeko_Tools/tools/(category folder)/music_player/
4. **Completely restart Blender** (not `F8` reload).
5. Open the N-panel in the 3D Viewport → `XNeko Tools` tab → find the module under its category.

No `pip`, no internet connection, and no global installation required — all dependencies are bundled inside each module.

---

## 🧩 Module Structure

Each module follows the standard XNeko_Tools layout:

```
<category>/
+-- <module_name>/
    +-- __init__.py        # Registration entry point
    +-- _deps.py           # Bundled dependency loader
    +-- _libs/             # Bundled third-party libraries
    +-- _operators.py      # Blender operators
    +-- _panels.py         # UI panels
    +-- ...                # Helper modules
```

Files starting with `_` are treated as internal helpers and are skipped by the framework's auto-registration.

---

## 📄 License

Each module may carry its own license. Check the module folder for details. Bundled third-party libraries retain their original licenses.

---

## 🔗 Related

- **Base toolbox:** [XNeko_Tools](https://github.com/XNeko258/XNeko_Tools)
- **Issues & feature requests:** please open an issue in the relevant repository.