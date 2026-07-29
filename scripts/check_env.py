"""Quick environment check."""
import sys; sys.path.insert(0, "src")
import torch
print(f"Python: {sys.version.split()[0]}")
print(f"torch: {torch.__version__}")
print(f"CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")

try:
    import peft
    print(f"peft: {peft.__version__}")
except ImportError:
    print("peft: NOT INSTALLED")

try:
    import datasets
    print(f"datasets: {datasets.__version__}")
except ImportError:
    print("datasets: NOT INSTALLED")

try:
    import transformers
    print(f"transformers: {transformers.__version__}")
except ImportError:
    print("transformers: NOT INSTALLED")
