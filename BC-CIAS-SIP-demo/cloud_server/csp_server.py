from flask import Flask, request, jsonify
import hashlib
import boto3

app = Flask(__name__)

# AWS S3 CONFIG
BUCKET_NAME = "bc-cias-sip-storage"
s3 = boto3.client("s3")

@app.route("/challenge", methods=["POST"])
def challenge():
    data = request.get_json()
    indices = data.get("indices", [])

    blocks = []

    for i in indices:
        key = f"blocks/block_{i}.bin"
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        block_data = obj["Body"].read()
        blocks.append(block_data.hex())

    combined = b"".join(bytes.fromhex(b) for b in blocks)
    proof = hashlib.sha256(combined).hexdigest()

    return jsonify({
        "blocks": blocks,
        "proof": proof
    })


# 🔥 THIS PART WAS MISSING 🔥
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
