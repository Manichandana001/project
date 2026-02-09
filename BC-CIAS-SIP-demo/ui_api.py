from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import sys
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_FILE = os.path.join(BASE_DIR, "audit_manifest.json")

# -------------------------
# Initialize manifest
# -------------------------
def init_manifest():
    if not os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "w") as f:
            json.dump([], f)

# -------------------------
# Upload + Sanitization
# -------------------------
@app.route("/api/upload", methods=["POST"])
def upload_file():
    try:
        print("\n[KGC] System parameters assumed initialized (prototype abstraction)")

        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        sensitive_fields = request.form.get("sensitive_fields")

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        if not sensitive_fields:
            return jsonify({"error": "No sensitive fields provided"}), 400

        fields = [f.strip() for f in sensitive_fields.split(",") if f.strip()]

        # Data Owner step
        print("[DO] File received from Data Owner")
        print("[DO] Audit tags (sigma) will be generated after sanitization")

        data_owner_dir = os.path.join(BASE_DIR, "data_owner")
        os.makedirs(data_owner_dir, exist_ok=True)

        original_filename = file.filename
        file_path = os.path.join(data_owner_dir, "sample.txt")
        file.save(file_path)

        # Sanitization
        print("[SANITIZER] Sensitive fields identified:", fields)
        print("[SANITIZER] Blinding sensitive data (F -> F*)")

        proc = subprocess.run(
            [sys.executable, "sanitize_and_upload.py", ",".join(fields)],
            cwd=data_owner_dir,
            capture_output=True,
            text=True
        )

        if proc.returncode != 0:
            return jsonify({"error": "Sanitization failed"}), 500

        print("[SANITIZER] Retagging completed on blinded file F*")

        # Register file for auditor
        init_manifest()
        with open(MANIFEST_FILE, "r") as f:
            manifest = json.load(f)

        manifest.append({
            "filename": "sanitized_sample.txt",
            "original_name": original_filename,
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        with open(MANIFEST_FILE, "w") as f:
            json.dump(manifest, f, indent=2)

        print("[SYSTEM] Blinded file F* registered for auditing")

        return jsonify({
            "message": "Blinded file F* uploaded and registered successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# List files for auditor
# -------------------------
@app.route("/api/list_files", methods=["GET"])
def list_files():
    init_manifest()
    with open(MANIFEST_FILE, "r") as f:
        manifest = json.load(f)

    return jsonify([item["filename"] for item in manifest]), 200

# -------------------------
# Run audit
# -------------------------
@app.route("/api/run_audit", methods=["POST"])
def run_audit():
    try:
        data = request.get_json()
        filename = data.get("filename")

        if not filename:
            return jsonify({"error": "Filename missing"}), 400

        print("\n[AUDIT] Audit challenge initiated for blinded file F*")
        print("[CSP] Requested to generate audit proof (sigma)")

        auditor_dir = os.path.join(BASE_DIR, "auditor")

        proc = subprocess.run(
            [sys.executable, "audit_client.py", filename],
            cwd=auditor_dir,
            capture_output=True,
            text=True
        )

        print(proc.stdout)
        if proc.stderr:
            print("[AUDITOR STDERR]", proc.stderr)

        if proc.returncode != 0:
            return jsonify({
                "error": "Audit failed",
                "stdout": proc.stdout,
                "stderr": proc.stderr
            }), 500

        print("[BLOCKCHAIN] Audit result recorded on blockchain")

        return jsonify({"output": proc.stdout}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
