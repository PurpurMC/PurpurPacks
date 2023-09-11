#!/bin/bash

datapack_prefix="purpurpack_"
datapack_folder="packs"
modrinth_api_route="https://api.modrinth.com/v2/version"

if [ -z "$MODRINTH_TOKEN" ]; then
    echo "The required environment variable MODRINTH_TOKEN is not set."
    exit 1
fi

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

    zipped_file_name="${datapack_prefix}${datapack_name}_$(jq '.version_number' <<< $modrinth_json).zip"

    #create a zipped file inside packs/<datapack>/dist/ without including the modrinth.json file & dist/ directory
    (cd $datapack_path && mkdir -p dist && zip -r "dist/${zipped_file_name}" . -x dist/ modrinth.json)

    echo "Datapack located at: $(ls ${datapack_path}/dist)"

    #TODO: check if project version already exists. if it does, then PATCH, otherwise, POST
    curl_output=$(curl -vs -H "Authorization: $MODRINTH_TOKEN" -X POST $modrinth_api_route -F data=$modrinth_json -F file="@${$datapack_path}/dist/${zipped_file_name}" 2>&1)


    error=$(jq '.error' <<< $curl_output)
    if [ $error == "null" ]; then
      echo -e "Successfully uploaded $datapack_name! Output:\n$(jq <<< $curl_output)"
      exit 0
    else
      echo -e "Failed to upload $datapack_name. Output:\n$(jq <<< $curl_output)"
      exit 1
    fi
done
