import os
import json
import zipfile

import requests

# Constants
datapack_prefix = "purpurpack_"
datapack_folder = "packs"
user_agent = "Deploy/Purpur/PurpurPacks (https://purpurmc.org/)"
modrinth_post_version_route = "https://api.modrinth.com/v2/version"
modrinth_token = os.getenv('MODRINTH_TOKEN')
DRY_RUN = True


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def log(msg):
    prefix = "[DRY RUN] " if DRY_RUN else ""
    print(prefix + msg)


DEFAULTS_DIR = os.path.dirname(__file__)

DATAPACK_DEFAULTS = load_json(
    os.path.join(DEFAULTS_DIR, "datapack-modrinth.json")
)

FABRIC_DEFAULTS = load_json(
    os.path.join(DEFAULTS_DIR, "mod-fabric-modrinth.json")
)

FORGE_DEFAULTS = load_json(
    os.path.join(DEFAULTS_DIR, "mod-forge-modrinth.json")
)

FABRIC_METADATA_FILES = [
    "modrinth.json", "fabric.mod.json", "quilt.mod.json"
]

FORGE_METADATA_FILES = [
    "modrinth.json", "mods.toml", "neoforge.mods.toml"
]

def merge_modrinth_info(defaults, override):
    merged = defaults.copy()
    merged.update(override)
    return merged

def build_datapack_zipfile(root, version):
    relative = os.path.relpath(root, datapack_folder)
    name = f"{relative.replace(os.sep, '_')}_v{version}.zip"

    out_directory = os.path.join(datapack_folder, "distro_datapack")
    os.makedirs(out_directory, exist_ok=True)

    path = os.path.join(out_directory, name)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, _, files in os.walk(root):
            for file in files:
                if file in FORGE_METADATA_FILES or file in FABRIC_METADATA_FILES:
                    continue
                z.write(
                    os.path.join(rel, file),
                    arcname=os.path.relpath(os.path.join(rel, file), root)
                )

    return path, name


def build_mod_jar(root, version):
    relative = os.path.relpath(root, datapack_folder)
    name = f"{relative.replace(os.sep, '_')}_v{version}.jar"

    out_dir = os.path.join(datapack_folder, "dist_mod")
    os.makedirs(out_dir, exist_ok=True)

    path = os.path.join(out_dir, name)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, _, files in os.walk(root):
            for file in files:
                if file == "modrinth.json":
                    continue
                z.write(
                    os.path.join(rel, file),
                    arcname=os.path.relpath(os.path.join(rel, file), root)
                )

    return path, name

def post_version(modrinth_data, file_path, file_name):
    if DRY_RUN:
        log("Would upload:")
        log(f"  File: {file_name}")
        log(f"  Project: {modrinth_data.get('project_id')}")
        log(f"  Version: {modrinth_data.get('version_number')}")
        log(f"  Loaders: {modrinth_data.get('loaders')}")
        log(f"  Game versions: {modrinth_data.get('game_versions')}")
        log(f"  Dependencies: {modrinth_data.get('dependencies')}")
        log("")
        return
    headers = {
        "Authorization": modrinth_token,
        "User-Agent": user_agent
    }

    with open(file_path, "rb") as f:
        response = requests.post(
            modrinth_post_version_route,
            headers=headers,
            files={"file": (file_name, f, "application/zip")},
            data={"data": json.dumps(modrinth_data)}
        )

    try:
        res = response.json()
    except Exception:
        print("Invalid Modrinth response")
        return

    if "error" in res:
        print(f"Upload failed for {file_name}: {res}")
    else:
        print(f"Uploaded {file_name} successfully")


def main():
    for root, _, files in os.walk(datapack_folder):
        if "pack.mcmeta" not in files or "modrinth.json" not in files:
            continue

        pack_meta = load_json(os.path.join(root, "modrinth.json"))
        version = pack_meta.get("version_number")

        if not version:
            print(f"{root} has no version_number, skipping")
            continue

        # =====================
        # DATAPACK
        # =====================
        dp_meta = merge_modrinth_info(pack_meta, DATAPACK_DEFAULTS)
        dp_path, dp_name = build_datapack_zipfile(root, version)
        post_version(dp_meta, dp_path, dp_name)

        # =====================
        # MOD JAR (build once)
        # =====================
        jar_path, jar_name = build_mod_jar(root, version)

        # Fabric / Quilt
        fabric_meta = merge_modrinth_info(pack_meta, FABRIC_DEFAULTS)
        post_version(fabric_meta, jar_path, jar_name)

        # Forge / NeoForge
        forge_meta = merge_modrinth_info(pack_meta, FORGE_DEFAULTS)
        post_version(forge_meta, jar_path, jar_name)



if __name__ == "__main__":
    main()