"""Run all tests: python run_checks.py"""
from p3_env import *
from starter import *

check_task1(build_tree, print_tree)

check_task2(build_tree, find_dfs, build_index, find_indexed)

check_task3(build_tree, compute_sizes, build_index, add_file, delete_file, find_indexed)

check_task4(build_tree, MinHeap, largest_files)
