# Project 3 — Directory Tree: Search and Folder Sizes: Starter Kit

Read the project handout first. This kit gives you the "environment" so you can spend your time on the algorithms.

## Files
| File | What it is | Edit? |
|---|---|---|
| `starter.py` | **Your code.** Every function with a `TODO` is one of the required tasks. | yes |
| `p3_env.py` | Provided environment: the `Node` class with `full_path` and `get_node`, input reader, file-system generator, `scan_folder` for a real folder, random queries and updates, checkers, timing and plotting helpers. | no |
| `run_checks.py` | Runs the tests for all tasks (handout example + random tests against brute force). | no |
| `run_example.py` | Full report: tree, searches, folder sizes, an update, the largest files. | no |
| `run_experiment.py` | Experiment tables; saves `results/experiment.csv` and `results/experiment.png`. | sizes only |
| `data/` | `example.txt` (handout example), `random_200.txt`. | add your own |
| `Project_3_Directory_Tree_Colab.ipynb` | The same kit as one notebook for Google Colab. | yes |

## How to run
Python 3.9+ and matplotlib (for the plots).
```
python run_checks.py                          # tests: aim for all ✅
python run_example.py                         # report for data/example.txt
python run_example.py data/random_200.txt     # another input file
python run_experiment.py                      # experiment tables, CSV, and plot (needs about 1 GB of memory)
```
In Colab: upload the notebook (File → Upload notebook) and run it from the top.

A real folder as input (on your own computer):
```python
from p3_env import *
write_files("data/my_documents.txt", scan_folder(os.path.expanduser("~/Documents")))
```

## What you write (starter.py)
| Handout task | Functions |
|---|---|
| 1. Build and print the tree | `build_tree`, `print_tree` |
| 2. Find a file: DFS and hash index | `find_dfs`, `build_index`, `find_indexed` |
| 3. Folder sizes and updates | `compute_sizes`, `add_file`, `delete_file` |
| 4. k largest files with a min-heap | `MinHeap` (`push`, `pop`), `largest_files` |
| 5. Experiment | run `run_experiment.py` |

## Rules
Implement the tree operations and the min-heap yourself (no `heapq`, and do not sort all files to find the largest ones). Python's `dict` is the hash table for the index. You may add helper functions and change anything in `starter.py`, but keep the function names and arguments so the checkers still work. Passing the checkers is necessary but not the whole grade.
