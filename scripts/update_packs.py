import os
import json


# Function to increment the version number
def increment_version(version, major=False):
    major_version, minor_version = map(int, version.split('.'))
    if major:
        major_version += 1
        minor_version = 0
    else:
        minor_version += 1
    return f"{major_version}.{minor_version}"


# Function to update modrinth.json files, replacing old versions with new ones
def update_modrinth_files(directory, new_name, changelog, new_versions, major_version=False, update_version=True):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "modrinth.json":
                file_path = os.path.join(root, file)

                with open(file_path, 'r') as f:
                    data = json.load(f)

                # Update version number if required
                if update_version:
                    current_version = data.get("version_number", "1.0")
                    new_version = increment_version(current_version, major=major_version)
                    data["version_number"] = new_version
                else:
                    new_version = data.get("version_number", "1.0")  # Use current version if not updating

                # Update name with the version placeholder
                data["name"] = new_name.replace("{ver}", new_version)

                # Update changelog
                data["changelog"] = changelog

                # Replace old game versions with new ones
                data["game_versions"] = new_versions

                # Write the updated data back to the file
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)

                print(f"Updated {file_path}")


# Function to update pack.mcmeta files, allowing changes to pack_format, min_inclusive, and max_inclusive
def update_pack_mcmeta(directory, new_pack_format, new_min_inclusive, new_max_inclusive):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "pack.mcmeta":
                file_path = os.path.join(root, file)

                with open(file_path, 'r') as f:
                    data = json.load(f)

                # Update pack_format
                if "pack" in data:
                    data["pack"]["pack_format"] = new_pack_format

                    # Update supported_formats
                    if "supported_formats" in data["pack"]:
                        data["pack"]["supported_formats"]["min_inclusive"] = new_min_inclusive
                        data["pack"]["supported_formats"]["max_inclusive"] = new_max_inclusive

                    # Write the updated data back to the file
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=4)

                    print(f"Updated {file_path}")


# Example usage
directory = "/packs"
new_name = "v{ver} Update"
changelog = "Update to 1.21.4"
new_versions = ["1.21.4"]  # Replace the old versions with the new version here
major_version_increment = False  # Set to True to increment the major version
update_version = True  # Set to False to skip version updates
new_pack_format = 61  # New pack_format value for pack.mcmeta
new_min_inclusive = 57  # New min_inclusive value for pack.mcmeta
new_max_inclusive = 61  # New max_inclusive value for pack.mcmeta

# Update modrinth.json files, removing old versions
update_modrinth_files(directory, new_name, changelog, new_versions, major_version_increment, update_version)

# Update pack.mcmeta files with new pack_format, min_inclusive, and max_inclusive
update_pack_mcmeta(directory, new_pack_format, new_min_inclusive, new_max_inclusive)
