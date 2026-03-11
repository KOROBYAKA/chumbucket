import subprocess
from pathlib import Path
import shutil

def create_pubkeys(nodes):
    keypair_path = Path("pubkeys_solana")
    shutil.rmtree(keypair_path, ignore_errors=True)
    keypair_path.mkdir(exist_ok=True)

    pubkeys = []

    for i in range(0,nodes):
        save_path = keypair_path / f"{i}.json"
        #Generating Solana keypair
        result = subprocess.run(
            ["solana-keygen", "new", "--no-passphrase", "--outfile", save_path],
            check=True,
            capture_output=True,
            text=True
        )

        #Saving pubkey
        for line in result.stdout.splitlines():
            if line.startswith('pubkey'):
                pubkey = line.split("pubkey:")[1]
                pubkeys.append(pubkey)
                shutil.move(save_path, str(keypair_path / f"{pubkey}.json"))

    shutil.rmtree(keypair_path, ignore_errors=True)
    keypair_path.rmdir()

    return pubkeys