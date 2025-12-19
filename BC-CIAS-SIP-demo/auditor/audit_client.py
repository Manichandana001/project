import requests
import json
import hashlib
from web3 import Web3

# -------------------------
# CLOUD SERVER CONFIG
# -------------------------
CSP_URL = "http://54.255.58.42:5001/challenge"

OWNER_MANIFEST = "../data_owner/owner_manifest.json"

# -------------------------
# BLOCKCHAIN CONFIG
# -------------------------
GANACHE_RPC = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0xB768A09A10eD5c749148745d35dc2Af21144Cb6E"

ACCOUNT = "0xe16e7823060b9B1F85f877E55FE80aeA168842bD"
PRIVATE_KEY = "0xb7fc9ca246c4f528908ae411a0815d0321ceea35b48f53b51e8b9476159dc503"

w3 = Web3(Web3.HTTPProvider(GANACHE_RPC))

# Load contract ABI
with open("../blockchain/build/contracts/Audit.json", "r") as f:
    contract_json = json.load(f)
    abi = contract_json["abi"]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# -------------------------
# AUDIT HELPERS
# -------------------------
def compute_expected_proof(blocks_hex):
    combined = b"".join(bytes.fromhex(b) for b in blocks_hex)
    return hashlib.sha256(combined).hexdigest()

# -------------------------
# BLOCKCHAIN STORAGE
# -------------------------
def store_result_on_chain(result, proof):
    print("Storing audit result on blockchain...")

    tx = contract.functions.submitAudit(result, proof).build_transaction({
        "from": ACCOUNT,
        "nonce": w3.eth.get_transaction_count(ACCOUNT),
        "gas": 3000000,
        "gasPrice": w3.to_wei("1", "gwei"),
        "chainId": 1337
    })

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Transaction hash:", tx_hash.hex())
    print("Mined in block:", receipt.blockNumber)

# -------------------------
# MAIN AUDIT FLOW
# -------------------------
def main():
    print("Sending audit challenge to CSP...")

    payload = {"indices": [0]}
    response = requests.post(CSP_URL, json=payload)

    print("CSP status code:", response.status_code)

    if response.status_code != 200:
        print("CSP error response:", response.text)
        return False

    csp_response = response.json()
    print("CSP Proof Received:", csp_response["proof"])

    # Compute expected proof
    expected_proof = compute_expected_proof(csp_response["blocks"])
    print("Expected Proof Calculated:", expected_proof)

    result = (expected_proof == csp_response["proof"])

    print("==============================")
    print("AUDIT RESULT:", "PASS" if result else "FAIL")
    print("==============================")

    store_result_on_chain(result, csp_response["proof"])
    return result

if __name__ == "__main__":
    main()
