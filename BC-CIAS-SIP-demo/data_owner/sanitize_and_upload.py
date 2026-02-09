import os
import sys
import json
import hashlib
import boto3
import uuid

# -------------------------
# AWS S3 CONFIG
# -------------------------
BUCKET_NAME = "bc-cias-sip-storage"
s3 = boto3.client("s3")

# -------------------------
# SANITIZATION LOGIC
# -------------------------
def sanitize_lines(lines, sensitive_fields):
    sanitized = []
    for line in lines:
        for field in sensitive_fields:
            if line.lower().startswith(field.lower() + ":"):
                key, _ = line.split(":", 1)
                line = f"{key}: ****"
        sanitized.append(line)
    return sanitized

# -------------------------
# MAIN
# -------------------------
def main():
    if len(sys.argv) < 2:
        print("Sensitive fields not provided")
        sys.exit(1)

    sensitive_fields = sys.argv[1].split(",")
    upload_id = str(uuid.uuid4())[:8]

    # Read original file
    with open("sample.txt", "r") as f:
        lines = f.read().splitlines()

    # Sanitize selected fields
    sanitized_lines = sanitize_lines(lines, sensitive_fields)
    sanitized_text = "\n".join(sanitized_lines)

    # -------------------------
    # SAVE LOCALLY (FOR AUDIT)
    # -------------------------
    local_dir = "../data_owner"
    os.makedirs(local_dir, exist_ok=True)

    local_file = os.path.join(local_dir, "sanitized_sample.txt")
    with open(local_file, "w") as f:
        f.write(sanitized_text)

    # -------------------------
    # UPLOAD TO S3 (ONE FILE)
    # -------------------------
    s3_key = "sanitized_sample.txt"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=sanitized_text.encode()
    )

    # -------------------------
    # MANIFEST
    # -------------------------
    proof = hashlib.sha256(sanitized_text.encode()).hexdigest()

    manifest = {
        "upload_id": upload_id,
        "s3_key": s3_key,
        "hash": proof,
        "masked_fields": sensitive_fields
    }

    with open("owner_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print("Sanitized upload successful")
    print("UPLOAD_ID =", upload_id)
    print("PROOF =", proof)

if __name__ == "__main__":
    main()
