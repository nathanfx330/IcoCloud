IcoCloud

IcoCloud is a lightweight, zero-dependency Python tool that converts raw Point Cloud data (.PLY) into renderable 3D meshes (.OBJ).

It works by instancing a low-poly icosahedron (sphere) at every vertex position. This transforms invisible point data into solid geometry that can be rendered in software like Blender, Maya, Unity, or Unreal Engine.

✨ Features

Universal PLY Support: Handles both ASCII and Binary PLY files (Little/Big Endian) with variable header strides (ignores colors/normals safely).

LOD System: Built-in "Level of Detail" sampler to reduce dense clouds by 90%, 75%, or 50% using random sampling.

Geometry Normalization: Generates mathematically perfect unit spheres before scaling.

Zero Dependencies: Runs on pure Python standard libraries. No numpy or pandas required.

🚀 Installation

Ensure you have Python 3.x installed.

Download icocloud.py and place it in the folder containing your .ply files.

📖 Usage

Open your terminal or command prompt.

Navigate to the folder containing your script and PLY files.

Run the script:

code
Bash
download
content_copy
expand_less
python icocloud.py

Follow the prompts:

Select the PLY file from the detected list.

LOD Level: Choose how much data to keep (100%, 50%, 25%, 10%).

World Scale: Scale the positions (useful if your scan data is in meters but you are working in centimeters).

Configuration

You can adjust the size of the individual spheres by opening the script in a text editor and changing the parameter at the top:

code
Python
download
content_copy
expand_less
# Radius of each individual sphere
ICO_RADIUS = 0.01
🛠 Workflow Example

Scenario: You have a LIDAR scan room_scan.ply that is too dense (1 million points) and invisible in your render engine.

Run IcoCloud.

Select room_scan.ply.

Choose LOD 2 (Medium) to keep only 25% of points for a stylistic look.

The script generates room_scan_LOD2_ico.obj.

Import the .obj into Blender.

You now have a mesh object made of 250,000 spheres that creates a stylized "atomic" visualization of your room.

📂 Output Format

The script outputs a standard Wavefront .OBJ file.

Vertices: v x y z

Faces: f v1 v2 v3

Note: The output is a single baked mesh containing all spheres. It is not an instancer file.

📜 License

MIT License. Free to use for personal and commercial projects.
