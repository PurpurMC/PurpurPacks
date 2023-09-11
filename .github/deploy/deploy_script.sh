
packs_json="packs.json"
data=$(cat "$packs_json")
cd "../"
for pack in $(echo "$data" | jq -r '.packs | keys[]'); do
  echo "STARTING ITERATION OVER PACK - PACK VARIABLES:"
      index_number="$pack"
      echo "PACK VARIABLES INFO: 'index_number' = $index_number"
      pack_data=$(echo "$data" | jq -r ".packs[$pack]")
      echo "PACK VARIABLES INFO: 'pack_data' = $pack_data"
      directory_name=$(echo "$pack_data" | jq -r ".directory_name")
      echo "PACK VARIABLES INFO: 'directory_name' = $directory_name"
      version_number=$(echo "$pack_data" | jq -r ".version_number")
      echo "PACK VARIABLES INFO: 'version_number' = $version_number"

      zip_filename="${directory_name}_${version_number}.zip"
          echo "ZIP INFO: 'zip_filename' = $zip_filename"
          cd "../"
          cd "./packs/$directory_name" || exit  # Move into the directory
          zip -r "../../latest_releases/$zip_filename" ./*  # Include only the contents of the directory
          cd "../" || exit  # Move back to the original directory
done