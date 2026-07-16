with open("compiler/00_core/01_project_overview.toon", encoding="utf-8") as f:
    lines = f.readlines()
print(f"Total lines: {len(lines)}")
for i, l in enumerate(lines, 1):
    if "`" in l:
        print(f"Line {i}: {repr(l.rstrip())}")
