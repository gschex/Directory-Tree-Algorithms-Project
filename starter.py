"""Project 3: Directory Tree: Search and Folder Sizes -- your code.

Fill in every TODO (replace `raise NotImplementedError()`). Keep the function names and
arguments so that run_checks.py can test them. Then run:
    python run_checks.py           # tests (handout example + random tests)
    python run_example.py          # full report for data/example.txt (or another input file)
    python run_experiment.py       # doubling experiment, CSV and plot in results/
"""

from p3_env import *


# ============================================================================
# Task 1 — Build and print the tree
# ============================================================================

def build_tree(files):
    """Build the tree from (path, size) pairs and return the root folder."""
    root = Node(files[0][0].split("/")[0])
    # TODO: for every (path, size): split the path at "/"
    # TODO: walk down from the root, creating a folder Node for every missing folder (set parent and add it to children)
    # TODO: create the file Node (is_file=True, size=size) in the last folder
    raise NotImplementedError()
    return root


def print_tree(node, depth=0):
    """Print the tree below node (2 spaces per level, children sorted by name)."""
    # TODO: print the node: '  ' * depth + name + '/' for a folder, or name + ' (size KB)' for a file
    # TODO: for a folder: call print_tree on every child (sorted by name) with depth + 1
    raise NotImplementedError()


# ============================================================================
# Task 2 — Find a file by name: DFS and a hash index
# ============================================================================

def find_dfs(root, name):
    """All full paths of files called `name`, found by DFS; sorted."""
    # TODO: DFS over the whole tree (recursive or with a stack)
    # TODO: collect full_path(x) for every file x with x.name == name
    # TODO: return the sorted list
    raise NotImplementedError()


def build_index(root):
    """Hash table: file name -> set of full paths. Built with one DFS."""
    index = {}
    # TODO: DFS over the tree; for every file x add full_path(x) to the set index[x.name] (create the set the first time)
    raise NotImplementedError()
    return index


def find_indexed(index, name):
    """All full paths of files called `name`, from the index; sorted."""
    # TODO: look up the name in the index (an unknown name gives []) and return the sorted list of paths
    raise NotImplementedError()


# ============================================================================
# Task 3 — Folder sizes as a subtree property, and updates
# ============================================================================

def compute_sizes(node):
    """Set every folder's size to the total size inside it; return node's size. O(n)."""
    # TODO: a file just returns its size
    # TODO: a folder: size = sum of compute_sizes(child) over its children; store it in node.size and return it
    raise NotImplementedError()


def add_file(root, index, path, size):
    """Add a new file; update only its ancestors and the index."""
    # TODO: walk down the path from the root, creating missing folders (size 0)
    # TODO: create the file node and add path to the set index[name]
    # TODO: walk up the parent pointers from the file's folder to the root, adding size to every folder
    raise NotImplementedError()


def delete_file(root, index, path):
    """Delete a file; update only its ancestors and the index."""
    # TODO: find the file with get_node
    # TODO: remove it from its folder's children and its path from the index (delete the entry when the set becomes empty)
    # TODO: walk up from its folder to the root, subtracting its size
    raise NotImplementedError()


# ============================================================================
# Task 4 — The k largest files with your own min-heap
# ============================================================================

class MinHeap:
    """Binary min-heap stored in a list (Q[0] is the smallest item)."""

    def __init__(self):
        self.Q = []

    def __len__(self):
        return len(self.Q)

    def peek(self):
        """The smallest item (do not remove it)."""
        return self.Q[0]

    def push(self, item):
        # TODO: append the item at the end of Q
        # TODO: heapify up: while it is smaller than its parent (i - 1) // 2, swap them
        raise NotImplementedError()

    def pop(self):
        """Remove and return the smallest item."""
        # TODO: swap the root with the last item and remove the last item
        # TODO: heapify down from the root: swap with the smaller child (2i + 1 or 2i + 2) while that child is smaller
        # TODO: return the removed smallest item
        raise NotImplementedError()


def largest_files(folder, k):
    """The k largest files under folder as (size, full path), largest first. O(m log k)."""
    heap = MinHeap()
    # TODO: DFS over all files under folder (keep track of the full path)
    # TODO: if len(heap) < k: push (size, path); elif (size, path) > heap.peek(): pop, then push
    # TODO: pop everything (smallest first) and return the list reversed
    raise NotImplementedError()


# ============================================================================
# Full report (provided)
# ============================================================================

def analyze(source, find=("File4.txt",), k=2):
    """Full report for a file list (or text): the tree, searches, folder sizes, an update, and the k largest files. Provided."""
    files = read_files(source)
    root = build_tree(files)
    if len(files) <= 30:
        print_tree(root)
    else:
        print(f"{len(files)} files (tree not printed)")
    index = build_index(root)
    for name in find:
        print(f"\nFind {name}:")
        print("  DFS:  ", find_dfs(root, name))
        print("  index:", find_indexed(index, name))
    compute_sizes(root)
    folders = [x for x in sorted(walk_tree(root), key=full_path) if not x.is_file]
    print("\nFolder sizes (KB):", ", ".join(f"{full_path(x)} {x.size}" for x in folders[:12]),
          "..." if len(folders) > 12 else "")
    print(f"\nThe {k} largest files under {root.name}:", largest_files(root, k))
    return root, index
