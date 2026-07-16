"""
Convert YAML-based .toon files to spec-compliant TOON format
using the official toon_format library (toon-format/toon-python).
"""

import yaml, re, os, sys

COMPILER_DIR = "../compiler"

_KEYWORD_VALUES = {"null": None, "true": True, "false": False, "yes": True, "no": False, "on": True, "off": False}
_YAML_KEY_FIX = {None: "null", True: "true", False: "false"}


def _fix_data(data):
    """Post-process data: handle YAML conversions."""
    if isinstance(data, dict):
        out = {}
        for k, v in data.items():
            if not isinstance(k, str):
                k = _YAML_KEY_FIX.get(k, str(k))
            if isinstance(v, str) and "\n" in v:
                items = v.split("\n")
                cleaned = []
                for x in items:
                    xs = x.strip()
                    if xs:
                        cleaned.append(_KEYWORD_VALUES.get(xs.lower(), xs))
                if len(cleaned) > 1:
                    out[k] = cleaned
                elif len(cleaned) == 1:
                    out[k] = cleaned[0]
                else:
                    out[k] = None
            else:
                out[k] = _fix_data(v)
        return out
    elif isinstance(data, list):
        return [_fix_data(v) for v in data]
    return data


def _get_indent(line):
    return len(line) - len(line.lstrip())


def _is_key_line(stripped):
    """
    Determine if a stripped line is a YAML key definition.
    
    Returns (is_key, key_name, inline_value) where inline_value can be None.
    """
    # Line ending with :  -->  key: (block value follows)
    if stripped.endswith(":"):
        before_colon = stripped[:-1]
        # If there are spaces before colon, it's prose like "system that is:"
        if " " in before_colon:
            return (False, None, None)
        return (True, before_colon, None)
    
    # Check for inline key: value
    # Match: word at start of line followed by ": "
    m = re.match(r"^([\w_][\w_\-]*):\s+(.*)", stripped)
    if m:
        return (True, m.group(1), m.group(2))
    
    return (False, None, None)


def _parse_yaml_like(text):
    """
    Parse the loose YAML-like format used in these .toon files.
    
    Rules:
    - Lines ending with : are keys (single-word before colon)
    - Lines with inline key: value pairs
    - Prose lines with trailing colons (spaces before :) are treated as text
    - Indented lines without : are scalar values (multiple same-indent = list)
    - ### headers and # comments are removed
    """
    lines = text.split("\n")
    
    # Strip TOON/YAML fences
    bt = chr(96) * 3
    if lines and lines[0].strip() == bt + "toon":
        lines = lines[1:]
    lines = [l for l in lines if bt not in l]
    
    # Remove comment lines
    filtered = []
    for l in lines:
        s = l.strip()
        if re.match(r"^#+$", s) or re.match(r"^# ", s):
            continue
        filtered.append(l)
    
    lines = filtered
    
    def _flush(result, key, values):
        """Assign values to a key in result dict."""
        if result is None:
            result = {}
        if len(values) == 0:
            result[key] = None
        elif len(values) == 1:
            result[key] = values[0]
        else:
            result[key] = values
        return result
    
    def _make_value(val_str):
        """Convert string to typed value."""
        keyword_val = _KEYWORD_VALUES.get(val_str.lower())
        if keyword_val is not None:
            return keyword_val
        if val_str.isdigit():
            return int(val_str)
        if re.match(r"^\d+\.\d+$", val_str):
            return float(val_str)
        return val_str
    
    def _parse_block(start_idx, parent_indent):
        """Parse lines at > parent_indent into a dict (or list of values).
        
        Returns (data, end_idx)
        """
        result = None          # dict when keys found, None when only values
        current_key = None
        current_values = []
        leading_values = []    # values before first key in block
        
        i = start_idx
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            
            indent = _get_indent(line)
            if indent <= parent_indent:
                break
            
            stripped = line.strip()
            is_key, key_part, inline_val = _is_key_line(stripped)
            
            if is_key:
                # This is a YAML key
                # If we have accumulated values and are about to start a key,
                # flush the previous key first
                if current_key is not None:
                    result = _flush(result, current_key, current_values)
                    current_values = []
                
                # Handle leading values (values before first key in this block)
                if current_key is None and current_values:
                    # These are leading prose descriptions - store as description
                    leading_values = current_values
                    current_values = []
                
                current_key = key_part
                
                # Handle inline value (key: value)
                if inline_val is not None:
                    current_values = [_make_value(inline_val)]
                    # Don't look for sub-content - inline value means this key is done
                    result = _flush(result, current_key, current_values)
                    current_key = None
                    current_values = []
                    i += 1
                    continue
                
                # Check next non-blank line(s) for sub-content
                peek_idx = i + 1
                while peek_idx < len(lines):
                    if lines[peek_idx].strip():
                        break
                    peek_idx += 1
                if peek_idx < len(lines):
                    peek = lines[peek_idx]
                    peek_indent = _get_indent(peek)
                    if peek_indent > indent:
                        sub_data, end = _parse_block(peek_idx, indent)
                        result = _flush(result, current_key, [])
                        result[current_key] = sub_data
                        current_key = None
                        current_values = []
                        i = end
                        continue
                
                i += 1
                continue
            
            # Regular value line (prose, bare text, etc.)
            val = _make_value(stripped)
            current_values.append(val)
            i += 1
        
        # End of block - flush remaining key
        if current_key is not None:
            result = _flush(result, current_key, current_values)
        
        # If we had no keys at all, return as list/scalar
        if result is None and current_values:
            # Combine with any leading values
            all_vals = leading_values + current_values
            if len(all_vals) > 1:
                return (all_vals, i)
            elif len(all_vals) == 1:
                return (all_vals[0], i)
            return (None, i)
        
        # If we HAD keys and have leading values, prepend them as description
        if result is not None and leading_values:
            desc = " ".join(str(v) for v in leading_values)
            if desc.strip():
                # Prepend description - move all existing keys into a sub-dict
                wrapped = {"description": desc}
                for k, v in result.items():
                    wrapped[k] = v
                result = wrapped
        
        if result is None:
            result = {}
        
        return (result, i)
    
    data, _ = _parse_block(0, -1)
    return data


def extract_data(path):
    """Read .toon file and return Python object."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    
    data = _parse_yaml_like(text)
    return _fix_data(data)


def convert_file(path):
    from toon_format import encode

    data = extract_data(path)
    if data is None:
        return ""
    result = encode(data)
    if not result.endswith("\n"):
        result += "\n"
    return result


if __name__ == "__main__":
    from toon_format import decode

    if len(sys.argv) >= 2 and sys.argv[1] == "--all":
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), COMPILER_DIR)
        paths = []
        for dirpath, _, filenames in os.walk(root):
            for f in filenames:
                if f.endswith(".toon"):
                    paths.append(os.path.join(dirpath, f))
        paths.sort()
    elif len(sys.argv) < 2:
        print("Usage: python toon_convert.py <file.toon> [file2.toon ...]")
        print("       python toon_convert.py --all")
        sys.exit(1)
    else:
        paths = [p for p in sys.argv[1:] if os.path.isfile(p)]

    ok = 0
    fail = 0
    for path in paths:
        try:
            result = convert_file(path)
            if not result.strip():
                print(f"EMPTY {path}")
                continue
            with open(path, "w", encoding="utf-8") as f:
                f.write(result)

            decoded = decode(result)
            print(f"OK  {path}")
            ok += 1
        except Exception as e:
            print(f"FAIL  {path}  {e}")
            fail += 1

    print(f"\n{ok} OK, {fail} failed out of {len(paths)} files")
