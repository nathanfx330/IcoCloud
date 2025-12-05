# IcoCloud

**IcoCloud** is a lightweight, zero-dependency Python tool that converts raw point cloud data (`.PLY`) into renderable 3D meshes (`.OBJ`).

It works by instancing a low-poly icosahedron (sphere) at every vertex position. This transforms invisible point data into solid geometry ready for Blender, Maya, Unity, or Unreal Engine.

> **Why use this?**  
> Raw point clouds often don’t render in standard 3D pipelines. IcoCloud turns them into stylized, atomic meshes that react to lighting and shadows.

---

## ✨ Features

- **Vertical Crop (RAM Saver):** Interactively slice away the top and bottom of your cloud (e.g., ceilings/floors) *before* processing to save huge amounts of RAM.
- **Axis Presets:** One-click fix for the “rotated -90°” problem. Convert Z-Up scans to Blender Y-Up automatically.
- **LOD System:** Built-in “Level of Detail” sampler to reduce dense clouds by 50%, 90%, or 99% using random sampling.
- **Universal PLY Support:** Handles ASCII and Binary PLY (Little/Big Endian) and safely ignores color/normal metadata.
- **Zero Dependencies:** Pure Python — no `numpy`, no `pandas`, no external libs.

---

## 🚀 Installation

1. Ensure **Python 3.x** is installed.  
2. Download `icocloud.py` and place it in the same folder as your `.ply` files.

---

## 📖 Usage

1. Open a terminal or command prompt.  
2. Navigate to the folder with your script and PLY files.  
3. Run:

```bash
python icocloud.py
````

4. **Follow the prompts:**

   * **Select File:** Choose from detected PLY files.
   * **Select Preset:**

     * `1` — **Blender / Unity (Z-Up → Y-Up)**
     * `2` — **CAD / Raw (no axis changes)**
   * **Height Crop:** Enter min/max height to keep (or press Enter to keep all).
   * **LOD Level:** Select how much of the point cloud to keep (e.g., 10%).
   * **World Scale:** Adjust global scale (default `1.0`).
   * **Sphere Radius:** Change sphere size (default `0.01`).

---

## 🛠 Configuration

You can change the default sphere radius by editing the script:

```python
# Radius of each individual sphere
ICO_RADIUS = 0.01
```

---

## ⚡ Workflow Example

**Scenario:** You have a LIDAR scan `apartment_scan.ply` (≈2M points) that crashes Blender.

1. Run **IcoCloud**.
2. Select `apartment_scan.ply`.
3. Choose **Preset 1** so it imports upright in Blender.
4. **Crop:** Script reports a height range of `-2.0` → `15.0`.
   Enter `0.0` (bottom) and `2.5` (top) to remove ceiling and floor.
5. **LOD:** Select **10%** (LOD 3).
6. Script outputs `apartment_scan_CROPPED.obj`.
7. Import into Blender → you get a lightweight, stylized mesh ready to use.

---

## ⚠️ Performance Note

**Geometry Explosion:**

Converting points to meshes increases data massively:

* **1 point → 1 vertex**
* **1 IcoCloud sphere → 12 vertices / 20 faces**

Example:
A **500k** point cloud becomes a **10 million polygon** mesh.

Use **LOD** and **Crop** to avoid out-of-memory crashes.

---

## 📂 Output Format

The script exports standard Wavefront `.OBJ`:

* **Vertices:** `v x y z`
* **Faces:** `f v1 v2 v3`

**Note:**
Output is a *single baked mesh* containing all spheres — not an instanced mesh.

---

## 📜 License

MIT License — free for personal and commercial use.
