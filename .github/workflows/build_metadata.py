from loader_classes import LoaderDefaults


def build_modrinth_metadata(pack_meta: dict, loader: LoaderDefaults) -> dict:
    meta = loader.defaults.copy()
    for key, value in pack_meta.items():
        if key == "dependencies":
            continue
        meta[key] = value

    deps = [
        *loader.defaults.get("dependencies", []),
        *pack_meta.get("dependencies", []),
    ]
    if deps:
        meta["dependencies"] = deps

    version = meta.get("version_number")
    if not version:
        raise ValueError("version_number missing from metadata")

    if loader.suffix:
        meta["version_number"] = f"{version}-{loader.suffix}"

    return meta
