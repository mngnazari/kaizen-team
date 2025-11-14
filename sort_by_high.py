# -*- coding: utf-8 -*-
import os
import shutil
import trimesh

SOURCE_FOLDER = r"C:\sort_by_high"
DEST_BASE = os.path.join(SOURCE_FOLDER, "Sorted_By_Height")

def get_height_category(h):
    for i in range(1, 50):
        if h < (i + 1):
            return "{}-{}mm".format(i, i + 1)
    return "50mm_plus"

def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def unique_path(dest_dir, name):
    base, ext = os.path.splitext(name)
    candidate = os.path.join(dest_dir, name)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dest_dir, "{}_{}{}".format(base, counter, ext))
        counter += 1
    return candidate

def gather_stl_files(root_folder):
    stl_paths = []
    for root, dirs, files in os.walk(root_folder):
        if os.path.abspath(root).startswith(os.path.abspath(DEST_BASE)):
            continue
        for f in files:
            if f.lower().endswith(".stl"):
                stl_paths.append(os.path.join(root, f))
    return stl_paths

def process_stl_files():
    stl_files = gather_stl_files(SOURCE_FOLDER)
    category_files = {}

    for path in stl_files:
        fname = os.path.basename(path)
        print("---- Processing:", fname)

        try:
            mesh = trimesh.load_mesh(path, force='mesh')
            if mesh.is_empty:
                print("  >> Empty or invalid STL.")
                continue

            # ابعاد محورهای X,Y,Z
            x_len = mesh.extents[0]
            y_len = mesh.extents[1]
            z_len = mesh.extents[2]

            # محور کوتاه‌تر را ارتفاع فرض کن
            height = min(x_len, y_len, z_len)

            cat = get_height_category(height)
            print("  Height = {:.2f} mm → {}".format(height, cat))

            if cat not in category_files:
                category_files[cat] = []
            category_files[cat].append(path)

        except Exception as e:
            print("  !! Error reading {}: {}".format(fname, e))

    for cat, paths in category_files.items():
        dest_dir = ensure_folder(os.path.join(DEST_BASE, cat))
        for src in paths:
            fname = os.path.basename(src)
            dst = unique_path(dest_dir, fname)
            shutil.copy2(src, dst)

    # حذف فولدرهای خالی
    for folder in os.listdir(DEST_BASE):
        full_path = os.path.join(DEST_BASE, folder)
        if os.path.isdir(full_path) and not os.listdir(full_path):
            print("Removing empty folder:", full_path)
            shutil.rmtree(full_path)

    print("✅ Categorization complete.")

if __name__ == "__main__":
    process_stl_files()
