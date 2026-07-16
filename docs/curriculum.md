# Curriculum Module

Defines learning progression. 1 file in `src/compiler/curriculum/`.

## Difficulty Distribution

7 levels from D0 to D6:
- D0: Trivial
- D1: Easy
- D2: Medium
- D3: Hard
- D4: Expert
- D5: Master
- D6: Grandmaster

## Curriculum Graph

Prerequisite-based graph that orders knowledge items by difficulty. Used for stratified sampling during dataset generation.

## Sample Types

Each sample has a type (concept, exercise, project, quiz, etc.) with configurable weight for sampling distribution.

## Usage

```python
from compiler.curriculum.engine import CurriculumGraph

cg = CurriculumGraph()
cg.add_node("intro", difficulty=0)
cg.add_node("advanced", difficulty=3, prerequisites=["intro"])
```
