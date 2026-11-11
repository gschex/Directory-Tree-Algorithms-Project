"""Full report: python run_example.py [input file]"""
import sys
from p3_env import *
from starter import *

source = sys.argv[1] if len(sys.argv) > 1 else "data/example.txt"
try:
    root, index = analyze(source)
    if source == "data/example.txt":
        add_file(root, index, "Root/Folder1/SubFolder1/File6.txt", 25)
        print("\nAfter adding Root/Folder1/SubFolder1/File6.txt (25 KB):",
              ", ".join(f"{f} {get_node(root, f).size}" for f in ["Root/Folder1/SubFolder1", "Root/Folder1", "Root"]))
except NotImplementedError:
    print("⏳ Finish Tasks 1-4 in starter.py first.")
