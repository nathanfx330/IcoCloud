# ==========================================
#               IcoCloud v1.1
#   Converts PLY Point Clouds to OBJ Mesh
# ==========================================

import os
import math
import random
import struct
import sys

# ----------------- PARAMETERS -----------------
ICO_RADIUS = 0.01   # default radius

# ----------------- ICOSPHERE GEOMETRY -----------------
t = (1.0 + math.sqrt(5.0)) / 2.0
raw_verts = [
    (-1,  t, 0), (1,  t, 0), (-1, -t, 0), (1, -t, 0),
    (0, -1,  t), (0, 1,  t), (0, -1, -t), (0, 1, -t),
    ( t, 0, -1), ( t, 0, 1), (-t, 0, -1), (-t, 0, 1)
]

# Normalize
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

# ----------------- PARSER -----------------
def get_struct_char(prop_type):
    if prop_type in ['char', 'int8']: return 'b'
    if prop_type in ['uchar', 'uint8']: return 'B'
    if prop_type in ['short', 'int16']: return 'h'
    if prop_type in ['ushort', 'uint16']: return 'H'
    if prop_type in ['int', 'int32']: return 'i'
    if prop_type in ['uint', 'uint32']: return 'I'
    if prop_type in ['float', 'float32']: return 'f'
    if prop_type in ['double', 'float64']: return 'd'
    return None

def read_ply_vertices(path):
    verts = []
    with open(path, "rb") as f:
        header_lines = []
        while True:
            line = f.readline().strip()
            header_lines.append(line.decode('ascii'))
            if line == b"end_header": break

        vertex_count = 0
        is_binary = False
        is_big_endian = False
        props = []
        in_vertex_element = False
        
        for line in header_lines:
            parts = line.split()
            if not parts: continue
            if parts[0] == "format":
                if "binary_little_endian" in parts[1]: is_binary = True
                elif "binary_big_endian" in parts[1]: is_binary = True; is_big_endian = True
            elif parts[0] == "element":
                if parts[1] == "vertex":
                    vertex_count = int(parts[2])
                    in_vertex_element = True
                else: in_vertex_element = False
            elif parts[0] == "property" and in_vertex_element:
                dtype = parts[1]
                name = parts[-1]
                if dtype == "list": continue
                fmt_char = get_struct_char(dtype)
                if fmt_char: props.append((name, fmt_char))

        idx_map = {'x': -1, 'y': -1, 'z': -1}
        for i, (name, char) in enumerate(props):
            if name in idx_map: idx_map[name] = i

        if -1 in idx_map.values(): raise ValueError("PLY missing x, y, or z.")
        
        print(f"  -> Format: {'Binary' if is_binary else 'ASCII'} | Count: {vertex_count}")
        
        ix, iy, iz = idx_map['x'], idx_map['y'], idx_map['z']
        
        if is_binary:
            endian_char = ">" if is_big_endian else "<"
            struct_fmt = endian_char + "".join([p[1] for p in props])
            stride = struct.calcsize(struct_fmt)
            for _ in range(vertex_count):
                data = f.read(stride)
                if len(data) < stride: break
                u = struct.unpack(struct_fmt, data)
                verts.append((u[ix], u[iy], u[iz]))
        else:
            for _ in range(vertex_count):
                line_data = f.readline().split()
                if not line_data: break
                v = [float(val) for val in line_data]
                verts.append((v[ix], v[iy], v[iz]))
    return verts

# ----------------- PRESETS -----------------
def apply_preset(verts, preset_id):
    """
    Input is assumed to be Z-Up (Scan Data).
    """
    new_verts = []
    print("  -> Transforming Coords...")
    
    # PRESET 1: Standard OBJ (Y-UP)
    # Why? Blender/Unity importers expect Y-Up files. 
    # Even though Blender is Z-Up internally, it rotates OBJs on import.
    # So we must give it Y-Up data so it rotates correctly to Z-Up.
    if preset_id == 1:
        for x, y, z in verts:
            new_verts.append((x, z, -y))

    # PRESET 2: Raw (Z-UP)
    # Why? 3ds Max / CAD often treat Z as Z and don't rotate on import.
    elif preset_id == 2:
        return verts # Keep as is
            
    return new_verts

# ----------------- WRITER -----------------
def write_ico_spheres(out_file, verts, radius, world_scale):
    v_offset = 0
    total = len(verts)
    
    with open(out_file, "w") as out:
        out.write(f"# OBJ from PLY\n")
        
        for i, (vx, vy, vz) in enumerate(verts):
            if i % 2000 == 0:
                sys.stdout.write(f"\rWriting... {int((i/total)*100)}%")
                sys.stdout.flush()

            w_vx = vx * world_scale
            w_vy = vy * world_scale
            w_vz = vz * world_scale

            for (ix, iy, iz) in ico_verts_unit:
                px = w_vx + ix * radius
                py = w_vy + iy * radius
                pz = w_vz + iz * radius
                out.write(f"v {px:.6f} {py:.6f} {pz:.6f}\n")

            for (f1, f2, f3) in ico_faces_unit:
                out.write(f"f {v_offset+f1+1} {v_offset+f2+1} {v_offset+f3+1}\n")

            v_offset += len(ico_verts_unit)
            
    print("\rWriting... 100%   \n")

# ----------------- MAIN -----------------
def main():
    ply_files = [f for f in os.listdir("./") if f.lower().endswith(".ply")]
    if not ply_files: print("No .ply files found."); return

    print("Found .PLY files:")
    for i,f in enumerate(ply_files): print(f"{i}: {f}")

    try:
        idx = int(input("Select PLY file #: "))
        ply_name = ply_files[idx]
    except: print("Invalid."); return

    print("\nTARGET SOFTWARE PRESET:")
    print("1 = Blender / Unity / Maya")
    print("    (Converts to Y-Up so Blender's importer rotates it correctly)")
    print("2 = 3ds Max / Unreal / CAD")
    print("    (Keeps Raw Z-Up)")
    
    try:
        preset_in = input("Select Preset [1 or 2]: ")
        preset = int(preset_in) if preset_in.strip() else 1
    except ValueError: preset = 1

    print("\nLOD LEVELS:")
    print("0 = 100%")
    print("1 = 10%")
    print("2 = 25%")
    print("3 = 50%")
    
    try:
        lod_in = input("Choose LOD [Default=0]: ")
        lod = int(lod_in) if lod_in.strip() else 0
    except ValueError: lod = 0

    lod_map = {0:1.0, 1:0.10, 2:0.25, 3:0.50}
    keep_ratio = lod_map.get(lod, 1.0)

    print(f"\nReading {ply_name}...")
    try:
        verts = read_ply_vertices(ply_name)
    except Exception as e:
        print(f"Error: {e}")
        return

    verts = apply_preset(verts, preset)

    if keep_ratio < 1.0:
        target = int(len(verts) * keep_ratio)
        if target < 1: target = 1
        print(f"Applying LOD... keeping {target} points.")
        verts = random.sample(verts, target)

    try:
        s_scale = input("World Scale (default 1.0): ")
        w_scale = float(s_scale) if s_scale.strip() else 1.0
        
        s_rad = input(f"Sphere Radius (default {ICO_RADIUS}): ")
        ico_rad = float(s_rad) if s_rad.strip() else ICO_RADIUS
    except ValueError:
        w_scale = 1.0; ico_rad = ICO_RADIUS

    base = os.path.splitext(ply_name)[0]
    out_file = f"{base}_LOD{lod}.obj"

    print(f"Generating OBJ...")
    write_ico_spheres(out_file, verts, ico_rad, w_scale)
    print("DONE! Saved:", out_file)

if __name__ == "__main__":
    main()
