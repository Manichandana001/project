# sanitize_and_upload.py
import os
import json
from split_and_tag import split_file, tag_block

CSP_STORAGE = "../cloud_server/storage"  # Save blocks inside cloud_server/storage
os.makedirs(CSP_STORAGE, exist_ok=True)

def save_block_to_csp(block_bytes, index):
    filename = os.path.join(CSP_STORAGE, f"block_{index}.bin")
    with open(filename, "wb") as f:
        f.write(block_bytes)
    return filename

def main():
    blocks = split_file("sample.txt", 512)
    manifest = []

    for i, block in enumerate(blocks):
        # OPTION A: DO NOT BLIND ANY BLOCKS. Store real blocks.
        saved_path = save_block_to_csp(block, i)

        manifest.append({
            "index": i,
            "saved_as": saved_path,
            "tag": tag_block(block),
            "masked": False
        })

    # Save manifest
    with open("owner_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print("\nUpload complete!")
    print("Manifest written to owner_manifest.json")

if __name__ == "__main__":
    main()
