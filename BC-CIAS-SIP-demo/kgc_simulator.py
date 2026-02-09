import json
import uuid
import hashlib

def kgc_setup():
    system_id = str(uuid.uuid4())
    master_seed = hashlib.sha256(system_id.encode()).hexdigest()

    params = {
        "system_id": system_id,
        "master_seed": master_seed,
        "description": "KGC simulated setup for BC-CIAS-SIP prototype"
    }

    with open("kgc_params.json", "w") as f:
        json.dump(params, f, indent=2)

    print("[KGC] Setup completed")
    print("[KGC] System ID generated")
    print("[KGC] Master seed generated")

if __name__ == "__main__":
    kgc_setup()
