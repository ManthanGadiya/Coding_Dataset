# Validation Module

> **v0.2.0-dev**

9-domain validation engine. 1 file in `src/compiler/validation/`.

## Validation Domains

| Domain | Checks |
|--------|--------|
| schema | Metadata present, ID present |
| graph | Knowledge atoms linked |
| reasoning | Reasoning chain exists, length >= 2 |
| fact | Factual correctness |
| execution | Executability |
| security | Security issues |
| consistency | Metadata/record domain match |
| dataset | Dataset-level checks |
| final | Release readiness |

## Usage

```python
from compiler.validation.engine import ValidationEngine

ve = ValidationEngine()
report = ve.validate(ekr_dict)
print(report.all_passed)  # True/False
for r in report.results:
    print(f"{r.domain}: {r.status}")
```

## Validation Status

Each domain returns: PASSED, FAILED, or WARNING. A report passes if all domains are PASSED or WARNING (no FATAL errors).
