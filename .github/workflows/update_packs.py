import json
import os

from config import DRY_RUN, datapack_folder, log

_raw_pack_format = os.getenv("PACK_FORMAT", "")
PACK_FORMAT: float | None = float(_raw_pack_format) if _raw_pack_format else None

_raw_min_format = os.getenv("MIN_FORMAT", "")
MIN_FORMAT: float | None = float(_raw_min_format) if _raw_min_format else None

INCREMENT_MAJOR = os.getenv("INCREMENT_MAJOR", "").lower() == "true"
VERSION_NUMBER = os.getenv("VERSION_NUMBER", "")
VERSION_NAME_TEMPLATE = os.getenv("VERSION_NAME_TEMPLATE", "v{version} Update")
CHANGELOG = os.getenv("CHANGELOG", "")
GAME_VERSIONS = [v.strip() for v in os.getenv("GAME_VERSIONS", "").split(",") if v.strip()]


def _increment_version(version: str) -> str:
    try:
        major, minor = map(int, version.split("."))
    except ValueError:
        return version
    if INCREMENT_MAJOR:
        return f"{major + 1}.0"
    return f"{major}.{minor + 1}"


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.write("\n")


def update_pack_mcmeta(path: str) -> None:
    data = _load_json(path)
    pack = data.get("pack")
    if not isinstance(pack, dict):
        print(f"Skipping {path}: missing 'pack' object")
        return

    if PACK_FORMAT is not None:
        existing_min = (
            pack.get("supported_formats", {}).get("min_inclusive")
            or pack.get("min_format")
        )
        new_min = MIN_FORMAT if MIN_FORMAT is not None else (existing_min if existing_min is not None else PACK_FORMAT)
        pack["pack_format"] = PACK_FORMAT
        pack["min_format"] = new_min
        pack["max_format"] = PACK_FORMAT

    effective_format = pack.get("pack_format", 0)
    if effective_format >= 82:
        pack.pop("supported_formats", None)
    elif PACK_FORMAT is not None:
        pack["supported_formats"] = {"min_inclusive": pack["min_format"], "max_inclusive": PACK_FORMAT}

    data["pack"] = pack

    log(f"{'Would update' if DRY_RUN else 'Updated'} {path}")
    if DRY_RUN:
        print(json.dumps(data, indent=4))
    else:
        _write_json(path, data)


_MIN_GAME_VERSION = (1, 21, 9)


def _parse_game_version(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return (0,)


def update_pack_meta(path: str) -> None:
    data = _load_json(path)

    new_version = VERSION_NUMBER or _increment_version(data.get("version_number", "1.0"))
    data["version_number"] = new_version
    data["name"] = VERSION_NAME_TEMPLATE.replace("{version}", new_version)

    if CHANGELOG:
        data["changelog"] = CHANGELOG

    if GAME_VERSIONS:
        existing = set(data.get("game_versions", []))
        merged = existing | set(GAME_VERSIONS)
        data["game_versions"] = sorted(
            (v for v in merged if _parse_game_version(v) >= _MIN_GAME_VERSION),
            key=_parse_game_version,
        )

    log(f"{'Would update' if DRY_RUN else 'Updated'} {path}")
    if DRY_RUN:
        print(json.dumps(data, indent=4))
    else:
        _write_json(path, data)


def main() -> None:
    if not os.path.isdir(datapack_folder):
        print(f"Directory '{datapack_folder}' does not exist")
        return

    log(f"Starting update scan of '{datapack_folder}'")

    for root, _, files in os.walk(datapack_folder):
        if "pack.mcmeta" not in files:
            continue

        update_pack_mcmeta(os.path.join(root, "pack.mcmeta"))

        if "pack-meta.json" in files:
            update_pack_meta(os.path.join(root, "pack-meta.json"))

    log("Finished update scan")


if __name__ == "__main__":
    main()
