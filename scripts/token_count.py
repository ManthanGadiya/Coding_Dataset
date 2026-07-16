import os
import sys

compiler_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../compiler")

if not os.path.isdir(compiler_dir):
    print(f"compiler directory not found at {compiler_dir}")
    sys.exit(1)

try:
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    use_tiktoken = True
except ImportError:
    use_tiktoken = False

files = []
for root, dirs, filenames in os.walk(compiler_dir):
    for f in filenames:
        if f.endswith(".toon"):
            files.append(os.path.join(root, f))

files.sort()

total_lines = 0
total_words = 0
total_chars = 0
total_tokens = 0

print("\n=== TOKEN COUNT REPORT ===\n")
print(f"{'File':<55} {'Lines':>7} {'Words':>7} {'Chars':>8} {'Tokens':>10}")
print("-" * 90)

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = len(content.splitlines())
    words = len(content.split())
    chars = len(content)
    tokens = len(enc.encode(content)) if use_tiktoken else int(words * 1.33)

    rel = os.path.relpath(fpath, os.path.dirname(compiler_dir))
    print(f"{rel:<55} {lines:>7} {words:>7} {chars:>8} {tokens:>10}")

    total_lines += lines
    total_words += words
    total_chars += chars
    total_tokens += tokens

print("-" * 90)
method = "tiktoken (cl100k_base)" if use_tiktoken else "words x 1.33 (approx)"
print(f"{f'TOTAL ({len(files)} files)':<55} {total_lines:>7} {total_words:>7} {total_chars:>8} {total_tokens:>10}")
print(f"\n* Token method: {method}")
if not use_tiktoken:
    print("  For precise count: pip install tiktoken")
