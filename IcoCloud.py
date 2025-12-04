# ==========================================
#               IcoCloud v1.0
#   Converts PLY Point Clouds to OBJ Mesh
# ==========================================

import os
import math
import random
import struct
import sys

# ----------------- PARAMETERS -----------------
ICO_RADIUS = 0.01   # radius of each ico sphere

# Generate Low-poly icosphere (icosahedron)
# Golden ratio
t = (1.0 + math.sqrt(5.0)) / 2.0

# Raw vertices (magnitude is approx 1.902, not 1.0)
raw_verts = [
    (-1,  t, 0), (1,  t, 0), (-1, -t, 0), (1, -t, 0),
    (0, -1,  t), (0, 1,  t), (0, -1, -t), (0, 1, -t),
    ( t, 0, -1), ( t, 0, 1), (-t, 0, -1), (-t, 0, 1)
]

# FIX 1: Normalize vertices so they lie exactly on a unit sphere (radius 1.0)
ico_verts_unit = []
for (x, y, z) in raw_verts:
    length = math.sqrt(x*x + y*y + z*z)
    ico_verts_unit.append((x/length, y/length, z/length))

ico_faces_unit = [
    (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
    (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
    (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
    (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)
]

# ----------------- PLY HELPER -----------------
def get_property_size(prop_type):
    """Returns byte size for PLY property types."""
    if prop_type in ['char', 'uchar', 'int8', 'uint8']: return 1
    if prop_type in ['short', 'ushort', 'int16', 'uint16']: return 2
    if prop_type in ['int', 'uint', 'float', 'int32', 'uint32', 'float32']: return 4
    if prop_type in ['double', 'float64']: return 8
    return 0

# ----------------- READ PLY -----------------
def read_ply_vertices(path):
    verts = []
    with open(path, "rb") as f:
        # Header Parsing
        line = ""
        header_lines = []
        while line != "end_header":
            line = f.readline().decode("ascii").strip()
            header_lines.append(line)

        # Parse Header info
        vertex_count = 0
        is_binary = False
        is_big_endian = False
        
        # We need to calculate stride (bytes per vertex) to skip colors/normals
        vertex_byte_size = 0
        in_vertex_element = False
        
        for line in header_lines:
            parts = line.split()
            if not parts: continue
            
            if parts[0] == "format":
                if "binary_little_endian" in parts[1]:
                    is_binary = True
                elif "binary_big_endian" in parts[1]:
                    is_binary = True
                    is_big_endian = True
            
            elif parts[0] == "element":
                if parts[1] == "vertex":
                    vertex_count = int(parts[2])
                    in_vertex_element = True
                else:
                    in_vertex_element = False
            
            elif parts[0] == "property" and in_vertex_element:
                # Assuming standard 'property float x' structure
                # Handling list properties (rare for vertex, usually face) is complex, skipped here.
                prop_type = parts[1]
                vertex_byte_size += get_property_size(prop_type)

        print(f"  -> Format: {'Binary' if is_binary else 'ASCII'}")
        print(f"  -> Count: {vertex_count}")
        if is_binary:
            print(f"  -> Stride: {vertex_byte_size} bytes per vertex")

        # Reading Data
        if is_binary:
            # FIX 2: Handle binary stride correctly
            # We assume x, y, z are the FIRST 3 properties. 
            # If they are float (4 bytes), that's 12 bytes.
            endian_char = ">" if is_big_endian else "<"
            fmt = endian_char + "fff" # Read 3 floats
            
            # The remaining bytes in this vertex (colors, normals, etc)
            remainder = vertex_byte_size - 12 

            for _ in range(vertex_count):
                data = f.read(12)
                if len(data) < 12: break
                x, y, z = struct.unpack(fmt, data)
                verts.append((x, y, z))
                
                if remainder > 0:
                    f.read(remainder) # Skip extra data
        else:
            # ASCII Reader
            for _ in range(vertex_count):
                line_data = f.readline().split()
                # Assuming first 3 columns are X Y Z
                x, y, z = map(float, line_data[:3])
                verts.append((x, y, z))

    return verts

# ----------------- WRITE OBJ -----------------
def write_ico_spheres(out_file, verts, radius=0.01, world_scale=1.0):
    v_offset = 0
    total = len(verts)
    
    with open(out_file, "w") as out:
        out.write(f"# OBJ generated from PLY pointcloud\n")
        out.write(f"# Total spheres: {total}\n")
        
        for i, (vx, vy, vz) in enumerate(verts):
            # Progress indicator for large files
            if i % 5000 == 0:
                sys.stdout.write(f"\rWriting... {int((i/total)*100)}%")
                sys.stdout.flush()

            # Apply world scale to position
            w_vx = vx * world_scale
            w_vy = vy * world_scale
            w_vz = vz * world_scale

            # Write vertices of ico sphere (radius applied locally)
            for (ix, iy, iz) in ico_verts_unit:
                px = w_vx + ix * radius
                py = w_vy + iy * radius
                pz = w_vz + iz * radius
                out.write(f"v {px:.6f} {py:.6f} {pz:.6f}\n")

            # Write faces
            for (f1, f2, f3) in ico_faces_unit:
                # Face indices are 1-based in OBJ
                out.write(f"f {v_offset+f1+1} {v_offset+f2+1} {v_offset+f3+1}\n")

            v_offset += len(ico_verts_unit)
            
    print("\rWriting... 100%   ")

# ----------------- MAIN -----------------
def main():
    # List PLY files
    ply_files = [f for f in os.listdir("./") if f.lower().endswith(".ply")]
    if not ply_files:
        print("No .ply files found in current directory.")
        return

    print("Found .PLY files:")
    for i,f in enumerate(ply_files):
        print(f"{i}: {f}")

    try:
        idx = int(input("Select the PLY file number: "))
        ply_name = ply_files[idx]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    print("\nLOD LEVELS (Random Sampling):")
    print("0 = original (100%)")
    print("1 = low    (10%)")
    print("2 = medium (25%)")
    print("3 = high   (50%)")
    
    try:
        lod = int(input("Choose LOD level: "))
    except ValueError:
        lod = 0

    lod_map = {0:1.0, 1:0.10, 2:0.25, 3:0.50}
    keep_ratio = lod_map.get(lod, 1.0)

    print(f"\nReading {ply_name}...")
    try:
        verts = read_ply_vertices(ply_name)
    except Exception as e:
        print(f"Error reading PLY: {e}")
        return

    print(f"Loaded {len(verts)} vertices.")

    if keep_ratio < 1.0:
        target = int(len(verts) * keep_ratio)
        if target < 1: target = 1
        print(f"Applying LOD... keeping {target} points.")
        verts = random.sample(verts, target)

    try:
        str_scale = input("Enter world scale for positions (default 1.0): ")
        world_scale = float(str_scale) if str_scale.strip() else 1.0
    except ValueError:
        world_scale = 1.0

    base = os.path.splitext(ply_name)[0]
    out_file = f"{base}_LOD{lod}_ico.obj"

    print(f"Generating ico spheres for {len(verts)} points...")
    print(f"Sphere Radius: {ICO_RADIUS}")
    print(f"Position Scale: {world_scale}")
    
    write_ico_spheres(out_file, verts, radius=ICO_RADIUS, world_scale=world_scale)
    print("DONE! Saved:", out_file)

if __name__ == "__main__":
    main()
