from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import json

# -------------------------
# Flask App Initialization
# -------------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------
# API: Get Manifest
# -------------------------
@app.route("/api/manifest", methods=["GET"])
def get_manifest():
    manifest_path = os.path.join(BASE_DIR, "data_owner", "owner_manifest.json")

    if not os.path.exists(manifest_path):
        return jsonify({"error": "Manifest not found"}), 404

    with open(manifest_path, "r") as f:
        data = json.load(f)

    return jsonify(data)


# -------------------------
# API: Upload & Sanitize
# -------------------------
@app.route("/api/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not file.filename.lower().endswith(".txt"):
            return jsonify({"error": "Only .txt files are allowed"}), 400

        data_owner_dir = os.path.join(BASE_DIR, "data_owner")
        os.makedirs(data_owner_dir, exist_ok=True)

        save_path = os.path.join(data_owner_dir, "sample.txt")
        file.save(save_path)

        print("File saved at:", save_path)

        # Run sanitize_and_upload.py
        proc = subprocess.run(
            ["python", "sanitize_and_upload.py"],
            cwd=data_owner_dir,
            capture_output=True,
            text=True
        )

        print("SANITIZE STDOUT:\n", proc.stdout)
        print("SANITIZE STDERR:\n", proc.stderr)

        if proc.returncode != 0:
            return jsonify({
                "error": "Sanitization failed",
                "details": proc.stderr
            }), 500

        return jsonify({
            "message": "Upload and sanitization successful"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# API: Run Audit
# -------------------------
@app.route("/api/run_audit", methods=["POST"])
def run_audit():
    try:
        auditor_dir = os.path.join(BASE_DIR, "auditor")

        proc = subprocess.run(
            ["python", "audit_client.py"],
            cwd=auditor_dir,
            capture_output=True,
            text=True
        )

        print("AUDIT STDOUT:\n", proc.stdout)
        print("AUDIT STDERR:\n", proc.stderr)

        if proc.returncode != 0:
            return jsonify({
                "error": "Audit execution failed",
                "details": proc.stderr
            }), 500

        return jsonify({"output": proc.stdout})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)

