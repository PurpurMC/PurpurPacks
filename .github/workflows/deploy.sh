#!/bin/bash

datapack_prefix="purpurpack_"
datapack_folder="packs"

base_modrinth_file_changed=$(jq 'map(select(startswith("modrinth.json")))|unique[]' <<< $ALL_CHANGED_FILES)

for datapack_path in $datapack_folder/*; do
    modrinth_file_path="$datapack_path/modrinth.json"

    # continue if not a directory
    if [ ! -d "$datapack_path" ]; then
      continue
    fi

    # continue if datapack folder does not include modrinth.json
    if [ ! -e "$modrinth_file_path" ]; then
      echo "No modrinth.json file located in \"$datapack_path\""
      continue
    fi

    # packs/<datapack> -> <datapack>
    datapack_name=$(cut -d'/' -f2 <<< $datapack_path)

    # continue if base modrinth file was not changed and the changed files do not include the datapack name
    if [ -z "$base_modrinth_file_changed" ] && [ -z $(jq "map(select(contains(${datapack_name})))|unique[]" <<< $ALL_CHANGED_FILES) ]; then
        continue
    fi


    # combine modrinth.json with <datapack>/modrinth.json (datapack file overrides base file values)
    modrinth_json=$(jq -s '.[0] * .[1]' modrinth.json $modrinth_file_path)

    #create a zipped file inside packs/<datapack>/dist/ without including the modrinth.json file & dist/ directory
    (cd $datapack_path && mkdir -p dist && zip -r "dist/${datapack_prefix}${datapack_name}_$(jq '.version_number' <<< $modrinth_json).zip" . -x dist/ modrinth.json)

    echo "Datapack located at: $(ls ${datapack_path}/dist)"
done
