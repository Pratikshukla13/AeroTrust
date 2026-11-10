import subprocess
import re
import sys

patterns = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)secret_key\s*=\s*['\"][^'\"]+['\"]"),
    re.compile(r"(?i)api[_-]?key\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]"),
    re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----"),
    re.compile(r"(?i)password\s*=\s*['\"][^'\"]{6,}['\"]"),
]

whitelist_terms = [
    "example", "placeholder", "dummy", "postgres:postgres", "password123",
    "test", "your_secret_here", "change_me", "localhost", "none", "null",
    "aerotrust_secret"
]

res = subprocess.run(["git", "log", "-p", "--full-history"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="ignore")
matches = []
for line in res.stdout.splitlines():
    if line.startswith("+") and not line.startswith("+++"):
        content = line[1:].strip()
        for p in patterns:
            match = p.search(content)
            if match:
                matched_str = match.group(0).lower()
                if any(w in matched_str for w in whitelist_terms):
                    continue
                matches.append((line[:120]))

print(f"Total potential secret scan matches: {len(matches)}")
for m in matches[:20]:
    print("MATCH:", m)

if matches:
    sys.exit(1)
print("Git history secret scan clean!")
