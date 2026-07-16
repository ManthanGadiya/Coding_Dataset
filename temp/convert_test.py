import yaml, json, re, sys

with open("../compiler/00_core/01_project_overview.toon", "r", encoding="utf-8") as f:
    raw = f.read()

lines = raw.split("\n")

# Remove leading/fencing and trailing backtick fence
if lines and lines[0].strip() == "```toon":
    lines = lines[1:]
if lines and lines[-1].strip() == "```":
    lines = lines[:-1]

# Filter comment-only lines
clean = []
for l in lines:
    s = l.strip()
    if re.match(r"^#+$", s):   # lines of only # characters
        continue
    if re.match(r"^# ", s):     # # comment lines
        continue
    clean.append(l)

text = "\n".join(clean)

try:
    data = yaml.safe_load(text)
    print(json.dumps(data, indent=2, default=str))
except yaml.YAMLError as e:
    print(f"YAML Error: {e}", file=sys.stderr)
    # Check what's on the problematic line
    if hasattr(e, 'problem_mark'):
        line_num = e.problem_mark.line
        print(f"Problem at line {line_num}: {repr(clean[line_num])}")
