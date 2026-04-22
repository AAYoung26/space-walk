# Space Walk

A cinematic, multimedia production centred around a black hole — combining 3D rendering, motion graphics, compositing, and sound design into a cohesive sci-fi short. Built entirely with Blender, DaVinci Resolve / Fusion, and ffmpeg.

---

## Project Overview

Space Walk is a personal creative endeavour with high production ambition, drawing visual and tonal inspiration from films like *Interstellar*, *Contact* (1997), *2001: A Space Odyssey*, *Event Horizon*, and *Gravity*.

The project runs the full production pipeline: asset creation and rendering in Blender, compositing and motion graphics in DaVinci Resolve Fusion, final edit assembly in DaVinci Resolve, and frame sequence processing via ffmpeg.

A retro sci-fi / CRT aesthetic (green phosphor terminal, Fallout-style boot sequences) runs through the interface and motion graphics elements, contrasting with the photorealistic 3D renders.

---

## Aims & Goals

- **Produce a cinematic black hole sequence** — a visually accurate, film-quality render of a black hole with an animated accretion disk, gravitational lensing, and a procedural star field, composited into a short cinematic piece.
- **Build a complete motion graphics package** — including a retro CRT loading screen, animated boot sequence, Space Walk logo, and a Sagittarius A* stats panel — all built natively in Fusion.
- **Achieve professional-grade visual effects** — crash zooms, pull-focus transitions, radial blur, and defocus effects referencing the cinematography of the benchmark films above.
- **Develop a broader solar system scene** — using real orbital data from the Solar System OpenData API and JPL Horizons API to populate a scientifically grounded Blender scene with 32 solar system bodies.
- **Create supporting tooling** — lightweight utilities (such as Frame Compiler) to streamline the production workflow.

---

## Production Components

### 3D / Rendering — Blender
- Procedural star field world shader (dual Voronoi approach)
- Animated accretion disk with Keplerian radial speed variation, driven by a polar coordinate shader and frame-based Value node driver
- Gravitational lensing refraction object
- Solar system data pipeline (32 bodies via JPL Horizons / NASA NSSDCA)

### Compositing / Motion Graphics — DaVinci Resolve Fusion
- Retro CRT loading screen with animated boot sequence
- Space Walk logo (3D extruded style using layered Text+ nodes with Glow)
- Animated loading bar
- Green wireframe black hole animation with travelling arc effects (Fusion expressions)
- Sagittarius A* stats panel with S–F tier rating system
- Cinematic zoom-in sequence with keyframed scale animation, radial blur, and lens defocus layers

### Post / Assembly — DaVinci Resolve
- Full edit assembly integrating rendered sequences, motion graphics, and audio
- Audio assets: boot-up SFX and terminal typing SFX

### Tooling
- **Frame Compiler** — a macOS desktop app (CustomTkinter + ffmpeg) for assembling PNG frame sequences into H.264 video clips, with progress tracking and a clean GUI

---

## Tools & Stack

| Area | Tool |
|---|---|
| 3D & Rendering | Blender (macOS), Cycles |
| Compositing & Motion Graphics | DaVinci Resolve 20 + Fusion |
| Video Processing | ffmpeg |
| Data Sources | Solar System OpenData API, JPL Horizons API, NASA NSSDCA |
| Sound | Mixkit, Pixabay |
| Tooling | Python, CustomTkinter, imageio-ffmpeg, PyInstaller |

---

## Repository Structure

```
space-walk/
├── blender/                 # Blender source file
├── raw_frames/              # PNG frame sequence outputs from Blender
│   ├── far_away/            # Frames 0001–0434
│   ├── zoom_in/             # Frames 0096–0144
│   ├── after_zoom_in/       # Frames 0482–0674
│   └── loading_screen/      # Frames 0001–0096
├── clips/                   # Compiled video segments
├── Music/                   # Music assets
├── SFX/                     # Sound effects
├── tools/
│   └── frame_compiler/      # Frame sequence → MP4 desktop utility
│       ├── frame_compiler.py
│       ├── frame_compiler.spec
│       └── requirements.txt
├── README.md
└── LICENSE
```

---

## Frame Compiler

A desktop app for compiling PNG frame sequences into `.mp4` videos.

### Requirements

- Python 3.12 (via Homebrew): `brew install python@3.12`
- Tk support: `brew install python-tk@3.12`

### Setup (first time only)

```bash
cd tools/frame_compiler
/opt/homebrew/bin/python3.12 -m venv venv
source venv/bin/activate
pip install imageio imageio-ffmpeg Pillow customtkinter pyinstaller
```

### Running

```bash
cd tools/frame_compiler
source venv/bin/activate
python3 frame_compiler.py
```

### Usage

1. Click **Browse…** to select a folder of frames — the starting frame and pattern are detected automatically
2. Choose a **Frame Rate**
3. Click **Save As…** to set the output file location
4. Click **Compile Video** — progress is shown while ffmpeg encodes
5. Click **Open Output** when done to preview the result

### Building a .app bundle

```bash
source venv/bin/activate
pyinstaller frame_compiler.spec
# Output: dist/Frame Compiler.app
```

On first launch, macOS Gatekeeper may warn about an unsigned app — right-click → Open → Open to bypass.

---

## License

MIT — see [LICENSE](LICENSE).
