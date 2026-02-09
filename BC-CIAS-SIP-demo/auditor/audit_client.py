import requests
import hashlib
import json
import boto3
import sys
from web3 import Web3

print("[AUDITOR] Audit client started")

# ===============================
# CSP CONFIG
# ===============================
CSP_URL = "http://54.255.58.42:5001/audit_hash"

# ===============================
# AWS S3 CONFIG
# ===============================
BUCKET_NAME = "bc-cias-sip-storage"
s3 = boto3.client("s3")

# ===============================
# BLOCKCHAIN CONFIG
# ===============================
GANACHE_RPC = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0xB768A09A10eD5c749148745d35dc2Af21144Cb6E"

ACCOUNT = "0x761Eb40A01CB2B4c6Eb37EEa5674B62D08676023"
PRIVATE_KEY = "0x8e3a4a59085c5b16c5a263861a830fcb1997ca8cef5f1a337e53b981c4ac5d55"

w3 = Web3(Web3.HTTPProvider(GANACHE_RPC))

with open("../blockchain/build/contracts/Audit.json") as f:
    abi = json.load(f)["abi"]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# ===============================
# MAIN AUDIT FLOW
# ===============================
def main():
    if len(sys.argv) < 2:
        print("No filename provided")
        return

    filename = sys.argv[1]
    print("[AUDITOR] Selected blinded file F*:", filename)

    # 1. Request CSP proof
    print("[AUDITOR] Sending audit challenge to CSP")
    r = requests.post(CSP_URL, json={"filename": filename})

    if r.status_code != 200:
        print("CSP error", r.status_code, r.text)
        return

    csp_proof = r.json()["proof"]
    print("[CSP] Generated audit tag (sigma):", csp_proof)

    # 2. Download file from S3
    print("[AUDITOR] Downloading blinded file F* from S3")
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
    file_data = obj["Body"].read()

    local_tag = hashlib.sha256(file_data).hexdigest()
    print("[AUDITOR] Locally computed audit tag (sigma):", local_tag)

    # 3. Compare
    result = (local_tag == csp_proof)
    print("AUDIT RESULT:", "PASS" if result else "FAIL")

    # 4. Store on blockchain
    print("[BLOCKCHAIN] Submitting audit result to smart contract")
    try:
        tx = contract.functions.submitAudit(result, csp_proof).build_transaction({
            "from": ACCOUNT,
            "nonce": w3.eth.get_transaction_count(ACCOUNT),
            "gas": 3000000,
            "gasPrice": w3.to_wei("1", "gwei"),
            "chainId": 1337
        })

        signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print("[BLOCKCHAIN] Audit stored immutably")
        print("Transaction Hash:", tx_hash.hex())
        print("Block Number:", receipt.blockNumber)
    except Exception as e:
        print("[BLOCKCHAIN ERROR]", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
