import sys
import os

print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Current working directory:", os.getcwd())

try:
    import PIL
    print("PIL version:", PIL.__version__)
except ImportError:
    print("PIL not installed")

print("Available modules:")
for module in sys.modules:
    print(f"- {module}")
