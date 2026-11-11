"""
Environment code for the CSCI 4100 group project (provided by the instructor).

You do not need to change this file. Your own code goes in starter.py
(or in the notebook cells marked TODO). This file gives you:
  * input readers and random data generators (fixed seeds, any size),
  * checkers that test your functions (the handout example + random tests),
  * timing helpers for the doubling experiment, and plotting helpers.
"""
import os, sys, io, csv, math, time, random, threading, contextlib

QUICK = os.environ.get("KIT_QUICK") == "1"     # smaller experiments (used only to test this kit)


def check(name, test):
    """Run one group of tests and print a one-line status."""
    try:
        run_with_big_stack(test)
        print(f"✅ {name}: all tests passed")
        return True
    except NotImplementedError:
        print(f"⏳ {name}: not implemented yet (finish the TODOs this test uses)")
    except AssertionError as e:
        print(f"❌ {name}: {e}")
    except Exception as e:
        print(f"❌ {name}: {type(e).__name__}: {e}")
    return False


def run_with_big_stack(fn, *args, **kwargs):
    """Call fn(*args, **kwargs) in a thread with a large stack, so that deep recursion
    (for example a recursive DFS on 10^5 vertices) does not crash Python."""
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 1_000_000))
    box = {}

    def target():
        try:
            box["value"] = fn(*args, **kwargs)
        except BaseException as e:            # re-raised in the caller below
            box["error"] = e

    old = None
    for mb in (512, 256, 64):                 # some systems refuse very large thread stacks
        try:
            old = threading.stack_size(mb * 1024 * 1024)
            break
        except (ValueError, RuntimeError):
            continue
    try:
        t = threading.Thread(target=target)
        t.start()
        t.join()
    finally:
        if old is not None:
            threading.stack_size(old)
    if "error" in box:
        raise box["error"]
    return box.get("value")


def capture_output(fn, *args, **kwargs):
    """Run fn and return everything it printed, as a string."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*args, **kwargs)
    return buf.getvalue()


def doubling_experiment(methods, sizes, make_input, repeat=3, max_size=None, prepare=None, label="n"):
    """Time every method on every input size and print a doubling table.

    methods   : dict  name -> function(input)
    sizes     : list of input sizes (each one double the previous one)
    make_input: function n -> input (made once per size, not timed)
    repeat    : number of runs per size; the table shows the average
    max_size  : dict  name -> largest size to run that method (for slow methods)
    prepare   : function input -> argument passed to each run (not timed), e.g. list
                to give every run a fresh copy when a method changes its input
    Returns a list of rows {n, method, seconds} for save_csv / plot_doubling.
    """
    max_size = max_size or {}
    prepare = prepare or (lambda data: data)
    names = list(methods)
    print(f"{label:>10} | " + " | ".join(f"{name:>26}" for name in names))
    print("-" * (12 + 29 * len(names)))
    rows, prev = [], {}
    for n in sizes:
        try:
            data = run_with_big_stack(make_input, n)
        except NotImplementedError:
            print(f"{n:>10} | " + " | ".join(f"{'(not implemented)':>26}" for _ in names))
            continue
        cells = []
        for name in names:
            if n > max_size.get(name, float("inf")):
                cells.append(f"{'(skipped: too slow)':>26}")
                continue
            try:
                total = 0.0
                for _ in range(repeat):
                    arg = prepare(data)
                    t0 = time.perf_counter()
                    run_with_big_stack(methods[name], arg)
                    total += time.perf_counter() - t0
            except NotImplementedError:
                cells.append(f"{'(not implemented)':>26}")
                continue
            t = total / repeat
            ratio = ""
            if name in prev and prev[name][0] * 2 == n and prev[name][1] > 0:
                ratio = f"x{t / prev[name][1]:.2f}"
            prev[name] = (n, t)
            rows.append({"n": n, "method": name, "seconds": t})
            cells.append(f"{t * 1000:>14.1f} ms {ratio:>8}")
        print(f"{n:>10} | " + " | ".join(cells), flush=True)
    return rows


def save_csv(rows, path):
    """Save experiment rows (list of dicts) as a CSV file for your report."""
    if not rows:
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("saved", path)


def _plt():
    import matplotlib
    if "ipykernel" not in sys.modules:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _finish(plt, path):
    if path:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print("saved", path)
    if "ipykernel" in sys.modules:
        plt.show()
    plt.close()


def plot_doubling(rows, title="", path=None):
    """Log-log plot of running time against n, one line per method."""
    if not rows:
        print("nothing to plot yet")
        return
    plt = _plt()
    plt.figure(figsize=(6, 4))
    for name in dict.fromkeys(r["method"] for r in rows):
        pts = [(r["n"], r["seconds"]) for r in rows if r["method"] == name]
        plt.loglog([p[0] for p in pts], [p[1] for p in pts], "o-", label=name)
    plt.xlabel("n")
    plt.ylabel("average time (s)")
    plt.title(title)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    _finish(plt, path)

# ===========================================================================
# Project 3: Directory Tree: Search and Folder Sizes
# ===========================================================================

EXAMPLE_TEXT = """\
# full path, size in KB
Root/Folder1/File1.txt, 10
Root/Folder1/File2.txt, 5
Root/Folder1/SubFolder1/File3.txt, 20
Root/Folder2/SubFolder1/SubFolder2/File4.txt, 15
Root/Folder2/File5.pdf, 30
"""

EXAMPLE_TREE_PRINT = """\
Root/
  Folder1/
    File1.txt (10 KB)
    File2.txt (5 KB)
    SubFolder1/
      File3.txt (20 KB)
  Folder2/
    File5.pdf (30 KB)
    SubFolder1/
      SubFolder2/
        File4.txt (15 KB)
"""


def parse_files(text):
    """Parse 'full path, size' lines. Returns a list of (path, size_kb)."""
    files = []
    for no, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        path, _, size = line.rpartition(",")
        if not path or not size.strip().isdigit():
            raise ValueError(f"line {no}: cannot parse {raw!r}")
        files.append((path.strip(), int(size)))
    return files


def read_files(path_or_text):
    """Read a file list from a file path (or directly from text in the same format)."""
    if "\n" in path_or_text:
        return parse_files(path_or_text)
    with open(path_or_text) as f:
        return parse_files(f.read())


def write_files(path, files):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write("# full path, size in KB\n")
        for p, s in files:
            f.write(f"{p}, {s}\n")


_FOLDERS = ["src", "docs", "data", "images", "old", "backup", "2024", "2025", "2026", "project", "notes",
            "music", "photos", "videos", "tmp", "lib", "test", "reports", "drafts", "shared", "classes", "work"]
_FILES = ["README.md", "notes.txt", "report.pdf", "data.csv", "main.py", "todo.txt", "index.html", "config.json"]
_PATTERNS = ["photo_{}.jpg", "song_{}.mp3", "slides_{}.pptx", "hw{}.pdf", "log_{}.txt", "video_{}.mp4", "scan_{}.png"]


def generate_files(n, seed=0, max_depth=8, files_per_folder=8):
    """Random file system with n files under 'Root', about n / files_per_folder folders, depth at most max_depth.
    File names repeat in different folders (README.md, photo_17.jpg, ...), like on a real computer.
    Returns a list of (path, size_kb)."""
    rng = random.Random(seed)
    folders = [("Root", 0)]
    child_names = [set()]
    for _ in range(max(0, n // files_per_folder - 1)):
        while True:
            i = rng.randrange(len(folders))
            if folders[i][1] < max_depth:
                break
        base = rng.choice(_FOLDERS)
        name, k = base, 1
        while name in child_names[i]:
            k += 1
            name = f"{base}_{k}"
        child_names[i].add(name)
        folders.append((folders[i][0] + "/" + name, folders[i][1] + 1))
        child_names.append(set())
    used = [set() for _ in folders]
    top = max(10, n // 20)
    common = min(0.3, 200 / max(1, n))       # at most about 200 files with the common names
    files = []
    while len(files) < n:
        i = rng.randrange(len(folders))
        if rng.random() < common:
            name = rng.choice(_FILES)
        else:
            name = rng.choice(_PATTERNS).format(rng.randint(1, top))
        if name in used[i] or name in child_names[i]:
            continue
        used[i].add(name)
        size = min(10 ** 7, int(rng.lognormvariate(4, 1.6)) + 1)
        files.append((folders[i][0] + "/" + name, size))
    return files


def scan_folder(root_dir, max_files=None):
    """Make a file list from a real folder on your computer (sizes in KB, at least 1).
    Example: files = scan_folder(os.path.expanduser("~/Documents"))"""
    root_dir = os.path.abspath(root_dir)
    root_name = os.path.basename(root_dir.rstrip(os.sep)) or "Root"
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames.sort()
        rel = os.path.relpath(dirpath, root_dir)
        prefix = root_name if rel == "." else root_name + "/" + rel.replace(os.sep, "/")
        for fn in sorted(filenames):
            try:
                size = os.path.getsize(os.path.join(dirpath, fn))
            except OSError:
                continue
            files.append((prefix + "/" + fn, max(1, (size + 1023) // 1024)))
            if max_files and len(files) >= max_files:
                return files
    return files


def random_queries(files, q, seed=0, missing=0.1):
    """q file names to search for: names of random files, plus about 10% names that do not exist."""
    rng = random.Random(seed)
    names = []
    for _ in range(q):
        if rng.random() < missing:
            names.append(f"missing_{rng.randrange(10 ** 6)}.txt")
        else:
            names.append(rng.choice(files)[0].rsplit("/", 1)[1])
    return names


def random_updates(files, u, seed=0):
    """u random updates that keep the file system valid: ("add", path, size) or ("delete", path)."""
    rng = random.Random(seed)
    current = dict(files)
    paths = list(current)
    folders = sorted({p.rsplit("/", 1)[0] for p in paths})
    ops = []
    for t in range(u):
        if paths and rng.random() < 0.5:
            i = rng.randrange(len(paths))
            p = paths[i]
            paths[i] = paths[-1]
            paths.pop()
            del current[p]
            ops.append(("delete", p))
        else:
            folder = rng.choice(folders)
            if rng.random() < 0.2:
                folder += f"/new_folder_{t}"
            p = f"{folder}/new_file_{t}.dat"
            size = rng.randint(1, 5000)
            current[p] = size
            paths.append(p)
            ops.append(("add", p, size))
    return ops


def apply_updates_to_list(files, ops):
    """The file list after the updates (used by the checkers)."""
    current = dict(files)
    for op in ops:
        if op[0] == "add":
            current[op[1]] = op[2]
        else:
            del current[op[1]]
    return list(current.items())


def write_example_files(folder="data"):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "example.txt"), "w") as f:
        f.write(EXAMPLE_TEXT)
    write_files(os.path.join(folder, "random_200.txt"), generate_files(200, seed=4100, max_depth=4))


# ---------- the tree node (used by your code and by the checkers) ----------

class Node:
    """A folder or a file in the directory tree."""
    __slots__ = ("name", "parent", "children", "is_file", "size")

    def __init__(self, name, parent=None, is_file=False, size=0):
        self.name = name
        self.parent = parent
        self.is_file = is_file
        self.size = size                              # file: its size; folder: total size inside (Task 3)
        self.children = None if is_file else {}       # folder: name -> Node

    def __repr__(self):
        return f"Node({self.name!r}, {'file' if self.is_file else 'folder'}, size={self.size})"


def full_path(node):
    """'Root/Folder1/File1.txt' for a node (walks up the parent pointers)."""
    parts = []
    while node is not None:
        parts.append(node.name)
        node = node.parent
    return "/".join(reversed(parts))


def get_node(root, path):
    """The node with this full path, or None."""
    parts = path.split("/")
    if parts[0] != root.name:
        return None
    node = root
    for name in parts[1:]:
        if node.is_file or name not in node.children:
            return None
        node = node.children[name]
    return node


def walk_tree(node):
    """All nodes below node (including node), in some order."""
    stack = [node]
    while stack:
        x = stack.pop()
        yield x
        if not x.is_file:
            stack.extend(x.children.values())


# ---------- brute force (used only by the checkers) -------------------------

def _bf_find(files, name):
    return sorted(p for p, s in files if p.rsplit("/", 1)[1] == name)


def _bf_folder_sizes(files):
    total = {}
    for p, s in files:
        parts = p.split("/")
        for i in range(1, len(parts)):
            f = "/".join(parts[:i])
            total[f] = total.get(f, 0) + s
    return total


def _bf_topk_sizes(files, folder, k):
    return sorted((s for p, s in files if p.startswith(folder + "/")), reverse=True)[:k]


# ---------- checkers --------------------------------------------------------

def check_task1(build_tree, print_tree):
    def test():
        files = parse_files(EXAMPLE_TEXT)
        root = build_tree(files)
        assert root.name == "Root" and not root.is_file, "the root must be the folder 'Root'"
        assert sorted(root.children) == ["Folder1", "Folder2"], f"children of Root: got {sorted(root.children)}"
        f4 = get_node(root, "Root/Folder2/SubFolder1/SubFolder2/File4.txt")
        assert f4 is not None and f4.is_file and f4.size == 15, "File4.txt should be a file of 15 KB"
        nodes = list(walk_tree(root))
        assert len(nodes) == 11, f"the example has 5 files and 6 folders, your tree has {len(nodes)} nodes"
        for x in nodes:
            if not x.is_file:
                for name, c in x.children.items():
                    assert c.name == name and c.parent is x, f"wrong name or parent pointer at {full_path(c)}"
        out = capture_output(print_tree, root)
        got = "\n".join(l.rstrip() for l in out.strip("\n").split("\n"))
        assert got == EXAMPLE_TREE_PRINT.strip("\n"), "print_tree output differs from the expected output:\n" + out
        for seed in range(5):
            files = generate_files(300, seed=seed)
            root = build_tree(files)
            assert sum(1 for x in walk_tree(root) if x.is_file) == len(files), "wrong number of files in the tree"
            for p, s in files[:50]:
                x = get_node(root, p)
                assert x is not None and x.is_file and x.size == s, f"{p} missing or wrong size"
    return check("Task 1: build and print the tree", test)


def check_task2(build_tree, find_dfs, build_index, find_indexed):
    def test():
        root = build_tree(parse_files(EXAMPLE_TEXT))
        want = ["Root/Folder2/SubFolder1/SubFolder2/File4.txt"]
        assert find_dfs(root, "File4.txt") == want, f"DFS search for File4.txt: got {find_dfs(root, 'File4.txt')}"
        assert find_dfs(root, "nope.txt") == [], "DFS search for a missing name must return []"
        index = build_index(root)
        assert find_indexed(index, "File4.txt") == want, "index search for File4.txt"
        assert find_indexed(index, "nope.txt") == [], "index search for a missing name must return []"
        assert find_dfs(root, "SubFolder1") == [], "only files are search results, not folders"
        for seed in range(5):
            files = generate_files(500, seed=seed)
            root = build_tree(files)
            index = build_index(root)
            for name in random_queries(files, 60, seed=seed):
                want = _bf_find(files, name)
                assert find_dfs(root, name) == want, f"DFS search for {name}: expected {want}"
                assert find_indexed(index, name) == want, f"index search for {name}: expected {want}"
    return check("Task 2: find a file (DFS and hash index)", test)


def check_task3(build_tree, compute_sizes, build_index, add_file, delete_file, find_indexed):
    def test():
        root = build_tree(parse_files(EXAMPLE_TEXT))
        total = compute_sizes(root)
        assert total == 80, f"total size of Root: expected 80, got {total}"
        want = {"Root": 80, "Root/Folder1": 35, "Root/Folder1/SubFolder1": 20, "Root/Folder2": 45,
                "Root/Folder2/SubFolder1": 15, "Root/Folder2/SubFolder1/SubFolder2": 15}
        for f, s in want.items():
            assert get_node(root, f).size == s, f"size of {f}: expected {s}, got {get_node(root, f).size}"
        index = build_index(root)
        add_file(root, index, "Root/Folder1/SubFolder1/File6.txt", 25)
        for f, s in {"Root/Folder1/SubFolder1": 45, "Root/Folder1": 60, "Root": 105, "Root/Folder2": 45}.items():
            assert get_node(root, f).size == s, f"after adding File6.txt, {f} should be {s}, got {get_node(root, f).size}"
        assert find_indexed(index, "File6.txt") == ["Root/Folder1/SubFolder1/File6.txt"], "add_file must update the index"
        add_file(root, index, "Root/Folder3/New/a.txt", 7)
        assert get_node(root, "Root/Folder3").size == 7 and root.size == 112, "add_file must create missing folders"
        delete_file(root, index, "Root/Folder1/SubFolder1/File6.txt")
        assert get_node(root, "Root/Folder1").size == 35 and root.size == 87, "delete_file must update the ancestors"
        assert get_node(root, "Root/Folder1/SubFolder1/File6.txt") is None, "the deleted file is still in the tree"
        assert find_indexed(index, "File6.txt") == [], "delete_file must update the index"
        for seed in range(4):
            files = generate_files(400, seed=seed)
            root = build_tree(files)
            compute_sizes(root)
            for f, s in _bf_folder_sizes(files).items():
                assert get_node(root, f).size == s, f"size of {f}: expected {s}"
            index = build_index(root)
            ops = random_updates(files, 200, seed=seed)
            for op in ops:
                if op[0] == "add":
                    add_file(root, index, op[1], op[2])
                else:
                    delete_file(root, index, op[1])
            after = apply_updates_to_list(files, ops)
            for f, s in _bf_folder_sizes(after).items():
                assert get_node(root, f).size == s, f"after random updates, size of {f}: expected {s}"
            for name in random_queries(after, 40, seed=seed):
                assert find_indexed(index, name) == _bf_find(after, name), f"index wrong for {name} after updates"
    return check("Task 3: folder sizes and updates", test)


def check_task4(build_tree, MinHeap, largest_files):
    def test():
        rng = random.Random(1)
        h, ref = MinHeap(), []
        for _ in range(2000):
            if ref and rng.random() < 0.4:
                ref.sort()
                assert h.peek() == ref[0], "peek must return the smallest item"
                assert h.pop() == ref.pop(0), "pop must remove and return the smallest item"
            else:
                x = (rng.randint(0, 50), str(rng.random()))
                h.push(x)
                ref.append(x)
            assert len(h) == len(ref), "len(heap) is wrong"
        root = build_tree(parse_files(EXAMPLE_TEXT))
        got = largest_files(root, 2)
        want = [(30, "Root/Folder2/File5.pdf"), (20, "Root/Folder1/SubFolder1/File3.txt")]
        assert got == want, f"example: expected {want}, got {got}"
        assert len(largest_files(root, 10)) == 5, "with k larger than the number of files, return all files"
        for seed in range(5):
            files = generate_files(600, seed=seed)
            root = build_tree(files)
            sizes = dict(files)
            folders = sorted({p.rsplit("/", 1)[0] for p, s in files})
            for folder in [folders[0]] + random.Random(seed).sample(folders, 5):
                for k in (1, 5, 40):
                    got = largest_files(get_node(root, folder), k)
                    assert [s for s, p in got] == _bf_topk_sizes(files, folder, k), \
                        f"largest {k} files in {folder}: wrong sizes or not largest first"
                    assert len({p for s, p in got}) == len(got), "a file appears twice"
                    for s, p in got:
                        assert p.startswith(folder + "/") and sizes.get(p) == s, f"{p} is not a file of size {s} in {folder}"
    return check("Task 4: MinHeap and the k largest files", test)
