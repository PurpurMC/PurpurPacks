import os
import json
import zipfile
import requests

# Constants
datapack_prefix = "purpurpack_"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
datapack_folder = os.path.join(REPO_ROOT, "packs")
distro_folder = os.path.join(REPO_ROOT, "distribute")
user_agent = "Deploy/Purpur/PurpurPacks (https://purpurmc.org/)"
modrinth_post_version_route = "https://api.modrinth.com/v2/version"
modrinth_token = os.getenv('MODRINTH_TOKEN')
DRY_RUN = os.getenv("DRY_RUN") == "true"
CI_SKIP = os.getenv("SKIP_CI") == "true"


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

_VERSION_CACHE = {}

def build_modrinth_metadata(base_meta, defaults, *, suffix=None):
    # Merge the info from the defaults into the metadata for the project specifically.
    # Will not override pack-specific defaults.
    meta = defaults.copy()
    for key, value in base_meta.items():
        if key == "dependencies":
            continue
        meta[key] = value

    # Merge the dependencies of the packs.
    # The 'overrides' will be appended, so they're not really overrides but whatever
    deps = []
    if "dependencies" in defaults:
        deps.extend(defaults["dependencies"])
    if "dependencies" in base_meta:
        deps.extend(base_meta["dependencies"])
    if deps:
        meta["dependencies"] = deps

    if suffix:
        base_version = meta.get("version_number")
        if not base_version:
            raise ValueError("version_number missing from metadata")
        # Modrinth doesn't let you use the same version multiple times. So it says the loader now.
        meta["version_number"] = f"{base_version}-{suffix}"

    return meta


def build_datapack_zipfile(root, version):
    relative = os.path.relpath(root, datapack_folder)
    name = f"{relative.replace(os.sep, '_')}_v{version}.zip"

    os.makedirs(distro_folder, exist_ok=True)

    path = os.path.join(distro_folder, name)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, _, files in os.walk(root):
            for file in files:
                if file in FORGE_METADATA_FILES or file in FABRIC_METADATA_FILES:
                    continue
                # noinspection PyTypeChecker
                z.write(
                    os.path.join(rel, file),
                    arcname=os.path.relpath(os.path.join(rel, file), root)
                )

    return path, name


def build_mod_jar(root, version, loader):
    relative = os.path.relpath(root, datapack_folder)
    name = f"{relative.replace(os.sep, '_')}_v{version}-{loader}.jar"

    os.makedirs(distro_folder, exist_ok=True)

    path = os.path.join(distro_folder, name)

    if loader == "fabric":
        excluded_files = FORGE_METADATA_FILES
    elif loader == "forge":
        excluded_files = FABRIC_METADATA_FILES
    else:
        raise ValueError(f"Unknown loader: {loader}")

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, _, files in os.walk(root):
            for file in files:
                if file in excluded_files:
                    continue
                # noinspection PyTypeChecker
                z.write(
                    os.path.join(rel, file),
                    arcname=os.path.relpath(os.path.join(rel, file), root)
                )

    return path, name

def fetch_existing_versions(project_id):
    if project_id in _VERSION_CACHE:
        return _VERSION_CACHE[project_id]

    url = f"https://api.modrinth.com/v2/project/{project_id}/version"
    headers = {
        "Authorization": modrinth_token,
        "User-Agent": user_agent
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to getch versions for project {project_id}")
        _VERSION_CACHE[project_id] = set()
        return _VERSION_CACHE[project_id]

    versions = response.json()
    existing = {
        v.get("version_number")
        for v in versions
        if "version_number" in v
    }
    _VERSION_CACHE[project_id] = existing
    return existing

def should_update(project_id, version_number):
    existing = fetch_existing_versions(project_id)

    if version_number in existing:
        log(f"Skipping {project_id} {version_number}: already exists on Modrinth")
        return False
    return True



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
    if CI_SKIP:
        print("CI-Skip detected, returning.")
        return
    # Hooray logging.
    log(f"Script dir: {SCRIPT_DIR}")
    log(f"Repo root: {REPO_ROOT}")
    log(f"Datapack folder: {datapack_folder}")
    log(f"Starting scan of '{datapack_folder}'")

    if not os.path.isdir(datapack_folder):
        log(f"Directory '{datapack_folder}' does not exist")
        return
    for root, _, files in os.walk(datapack_folder):
        if "pack.mcmeta" not in files:
            log(f"Skipping {root}: missing pack.mcmeta")
            continue

        if "modrinth.json" not in files:
            log(f"Skipping {root}: missing modrinth.json")
            continue

        pack_meta = load_json(os.path.join(root, "modrinth.json"))
        version = pack_meta.get("version_number")
        log(f"Found valid pack at {root}")

        if not version:
            print(f"{root} has no version_number, skipping")
            continue

        # Vanilla Datapack
        dp_meta = build_modrinth_metadata(pack_meta, DATAPACK_DEFAULTS)
        # If the version already exists, skip it. For simplicity sake we're only gonna check the datapack version.
        # This could be added to the other versions though, too.
        if not should_update(project_id=pack_meta.get('project_id'), version_number=pack_meta.get('version_number')):
            continue

        dp_path, dp_name = build_datapack_zipfile(root, version)
        post_version(dp_meta, dp_path, dp_name)

        # Fabric and Quilt
        fabric_meta = build_modrinth_metadata(pack_meta, FABRIC_DEFAULTS, suffix="fabric")
        fabric_path, fabric_name = build_mod_jar(root, version, "fabric")
        post_version(fabric_meta, fabric_path, fabric_name)

        # Forge & Neoforge
        forge_meta = build_modrinth_metadata(pack_meta, FORGE_DEFAULTS, suffix="forge")
        forge_path, forge_name = build_mod_jar(root, version, "forge")
        post_version(forge_meta, forge_path, forge_name)

        log("Finished scan")




if __name__ == "__main__":
    main()