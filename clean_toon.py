"""
Clean all .toon files to be directly parseable as YAML:
  - strip ```toon / ``` fences
  - remove comment-only lines
  - flatten > folded blocks to quoted strings
  - convert implicit lists (indented items without -) to explicit - lists
"""

import re, os, sys

COMPILER_DIR = "compiler"

def strip_fences(lines):
    if lines and lines[0].strip() == "```toon":
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return lines

def filter_comments(lines):
    out = []
    for l in lines:
        s = l.strip()
        if re.match(r"^#+$", s) or re.match(r"^# ", s):
            continue
        out.append(l)
    return out

def flatten_folded_blocks(text):
    """Replace YAML > folded blocks with inline quoted strings."""
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        l = lines[i]
        m = re.match(r"^(\s*[\w_]+):\s*>\s*$", l)
        if m:
            indent = m.group(1)
            parts = [l.replace(": >", ': "')]
            i += 1
            while i < len(lines):
                n = lines[i]
                if not n.strip():
                    i += 1
                    break
                n_indent = len(n) - len(n.lstrip())
                if n_indent <= len(indent):
                    break
                parts.append(n.strip())
                i += 1
            out.append(" ".join(parts) + '"')
            continue
        out.append(l)
        i += 1
    return "\n".join(out)

def convert_implicit_lists(text):
    """
    Convert YAML implicit lists to explicit - lists.
    
    A key: followed by indented lines without ':' means
    those lines are implicit list items.
    """
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\s*)([\w][\w_]*):\s*$", line)
        if m:
            indent_str = m.group(1)
            base_indent = len(indent_str)

            # look ahead to determine if children are list items or sub-keys
            j = i + 1
            children = []
            while j < len(lines):
                n = lines[j]
                if not n.strip():
                    j += 1
                    continue
                n_indent = len(n) - len(n.lstrip())
                if n_indent <= base_indent:
                    break
                children.append((j, n, n_indent))
                j += 1

            if children:
                # if every child has no ':', it is an implicit list
                is_list = True
                for _, cl, _ in children:
                    # skip if line is already a list item
                    if cl.lstrip().startswith("- "):
                        continue
                    # if line contains ':' it's a sub-key, not list item
                    if ":" in cl.lstrip():
                        is_list = False
                        break

                if is_list:
                    out.append(line)
                    i += 1
                    for idx, cl, n_indent in children:
                        if not cl.strip():
                            continue
                        if cl.lstrip().startswith("- "):
                            out.append(cl)
                        else:
                            out.append(" " * n_indent + "- " + cl.lstrip())
                        i = idx + 1
                    continue

        out.append(line)
        i += 1
    return "\n".join(out)

def clean_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    lines = strip_fences(lines)
    lines = filter_comments(lines)
    text = "\n".join(lines)
    text = flatten_folded_blocks(text)
    text = convert_implicit_lists(text)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    # verify it parses
    import yaml
    try:
        yaml.safe_load(text)
        return True, None
    except yaml.YAMLError as e:
        return False, str(e)

def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), COMPILER_DIR)
    toon_files = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".toon"):
                toon_files.append(os.path.join(dirpath, f))
    toon_files.sort()

    ok = 0
    fail = 0
    for fp in toon_files:
        rel = os.path.relpath(fp, os.path.dirname(root))
        success, err = clean_file(fp)
        if success:
            print(f"  OK  {rel}")
            ok += 1
        else:
            print(f"FAIL  {rel}  {err}")
            fail += 1

    print(f"\n{ok} cleaned, {fail} failed out of {ok+fail} files")

if __name__ == "__main__":
    main()
