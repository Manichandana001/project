from flask import Flask, request, jsonify
import boto3
import hashlib

app = Flask(__name__)

BUCKET_NAME = "bc-cias-sip-storage"
s3 = boto3.client("s3")

@app.route("/audit_hash", methods=["POST"])
def audit_hash():
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify({"error": "Filename missing"}), 400

    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
        file_data = obj["Body"].read()

        file_hash = hashlib.sha256(file_data).hexdigest()

        print("[CSP] Generated audit tag (sigma) for", filename)
        return jsonify({"proof": file_hash}), 200

    except Exception as e:
        print("[CSP ERROR]", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # 🚫 NO DEBUG MODE ON EC2
    app.run(host="0.0.0.0", port=5001)
