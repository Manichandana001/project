# split_and_tag.py
import hashlib

def split_file(filename, block_size=512):
    blocks = []
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(block_size)
            if not chunk:
                break
            blocks.append(chunk)
    return blocks

def tag_block(block):
    return hashlib.sha256(block).hexdigest()

if __name__ == "__main__":
    blocks = split_file("sample.txt", 512)
    tags = [tag_block(b) for b in blocks]
    print("Total Blocks:", len(blocks))
    for index, t in enumerate(tags):
        print(f"Block {index}: {t}")
