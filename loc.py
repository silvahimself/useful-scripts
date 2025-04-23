#!/usr/bin/env python3

import os
import sys
from collections import defaultdict

class LineCounter:
    def __init__(self, extensions, ignore_directories):
        self.extensions = extensions
        self.ignore_directories = ignore_directories
        self.lines_by_directory = defaultdict(int)
        self.lines_by_extension = defaultdict(int)

    def count_lines_in_directory(self, directory_path):
        if not directory_path or not isinstance(directory_path, str):
            raise ValueError("Directory path cannot be null or empty")
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory '{directory_path}' not found")
        
        total_lines = self._process_directory(directory_path)
        
        return total_lines, self.lines_by_extension, self.lines_by_directory
    
    def _process_directory(self, directory_path, base_dir=None):
        """
        Process a directory and count lines in files and subdirectories.
        
        Args:
            directory_path: Path to the directory to process
            base_dir: Base directory path for calculating relative paths
            
        Returns:
            Total number of lines in this directory and its subdirectories
        """
        if base_dir is None:
            base_dir = directory_path
            
        total_lines = 0
        first_level_dirs = {}
        
        try:
            for item in os.listdir(directory_path):
                full_path = os.path.join(directory_path, item)
                
                # Skip ignored directories
                if os.path.isdir(full_path):
                    dir_name = os.path.basename(full_path)
                    if dir_name in self.ignore_directories or dir_name.startswith('.'):
                        continue
                    
                    # Process subdirectory
                    dir_lines = self._process_directory(full_path, base_dir)
                    total_lines += dir_lines
                    
                    # Extract first level directory for tracking
                    rel_path = os.path.relpath(full_path, base_dir)
                    top_dir = rel_path.split(os.sep)[0]
                    first_level_dirs[top_dir] = first_level_dirs.get(top_dir, 0) + dir_lines
                
                # Process files
                elif os.path.isfile(full_path):
                    _, ext = os.path.splitext(full_path)
                    if ext in self.extensions:
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                lines = [line for line in f.read().splitlines() if line.strip()]
                                lines_count = len(lines)
                                total_lines += lines_count
                                self.lines_by_extension[ext] += lines_count
                                
                                # Add to first level directory count
                                rel_path = os.path.relpath(os.path.dirname(full_path), base_dir)
                                if rel_path == '.':
                                    # Files in the root directory
                                    first_level_dirs['.'] = first_level_dirs.get('.', 0) + lines_count
                                else:
                                    top_dir = rel_path.split(os.sep)[0]
                                    first_level_dirs[top_dir] = first_level_dirs.get(top_dir, 0) + lines_count
                        except Exception:
                            # Skip files that can't be read
                            continue
        
        except Exception as e:
            # Skip directories that can't be processed
            print(f"Warning: Couldn't process {directory_path}: {str(e)}", file=sys.stderr)
        
        # Update directory counts (only at the base level)
        if directory_path == base_dir:
            for dir_name, count in first_level_dirs.items():
                if dir_name != '.':
                    self.lines_by_directory[dir_name] = count
                    
            # If there were files in the root directory
            if '.' in first_level_dirs:
                self.lines_by_directory['(root directory)'] = first_level_dirs['.']
        
        return total_lines


def main():
    # Get target directory
    target_dir = os.getcwd()
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    
    try:
        extensions = [
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
            ".html",
            ".css",
            ".cs",
            ".c",
            ".cpp",
            ".h",
            ".py",
        ]
        
        ignore_directories = [
            "bin",
            "obj",
            "node_modules",
            "dist",
            "build",
            ".git",
            ".vs",
            ".vscode",
            "Migrations"
        ]
        
        counter = LineCounter(extensions, ignore_directories)
        total_lines, lines_by_extension, lines_by_directory = counter.count_lines_in_directory(target_dir)
        
        print(f"Total lines of code: {total_lines}")
        print("\nBreakdown by file type:")
        
        # Sort extensions by line count (descending)
        for ext, count in sorted(lines_by_extension.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ext}: {count} lines")
        
        print("\nBy directory:")
        # Sort directories by line count (descending)
        for directory, count in sorted(lines_by_directory.items(), key=lambda x: x[1], reverse=True):
            print(f"  -- {directory}: {count} lines")
            
        # Verify the totals match
        dir_total = sum(lines_by_directory.values())
        ext_total = sum(lines_by_extension.values())
        if total_lines != dir_total or total_lines != ext_total:
            print("\nWarning: Inconsistency in line counts detected:")
            print(f"  Total lines: {total_lines}")
            print(f"  Sum of directory counts: {dir_total}")
            print(f"  Sum of extension counts: {ext_total}")
    
    except Exception as ex:
        print(f"Error: {str(ex)}")


def run_tests():
    """Run some basic tests to verify the line counting logic."""
    print("Running tests...\n")
    
    all_tests_passed = True
    
    # Test 1: Simple directory structure
    print("TEST 1: Simple directory structure with files at different levels")
    print("----------------------------------------------------------------")
    
    test_dir = "loc_test_dir"
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)
    
    try:
        # Create test directory structure
        print("Creating test directory structure:")
        os.makedirs(os.path.join(test_dir, "dir1"))
        os.makedirs(os.path.join(test_dir, "dir2", "subdir"))
        
        # Create some test files
        test_files = [
            (os.path.join(test_dir, "root.py"), "line1\nline2\nline3\n", 3),
            (os.path.join(test_dir, "dir1", "file1.py"), "line1\nline2\n", 2),
            (os.path.join(test_dir, "dir2", "file2.py"), "line1\nline2\nline3\nline4\n", 4),
            (os.path.join(test_dir, "dir2", "subdir", "file3.py"), "line1\nline2\nline3\nline4\nline5\n", 5)
        ]
        
        for file_path, content, line_count in test_files:
            with open(file_path, "w") as f:
                f.write(content)
            print(f"  - Created {file_path} with {line_count} lines")
        
        # Count lines
        print("\nCounting lines in test directory...")
        counter = LineCounter(extensions=[".py"], ignore_directories=[])
        total_lines, lines_by_extension, lines_by_directory = counter.count_lines_in_directory(test_dir)
        
        # Expected results
        expected_total = 14  # 3 + 2 + 4 + 5
        expected_by_ext = {".py": 14}
        expected_by_dir = {"dir1": 2, "dir2": 9, "(root directory)": 3}
        
        # Verify results
        test1_passed = True
        
        print("\nChecking results:")
        print(f"  - Total lines: Expected {expected_total}, Got {total_lines}")
        if total_lines != expected_total:
            print(f"    ERROR: Total line count mismatch")
            test1_passed = False
            all_tests_passed = False
        else:
            print(f"    ✓ Total count correct")
        
        print(f"  - Lines by extension: Expected {expected_by_ext}, Got {dict(lines_by_extension)}")
        if dict(lines_by_extension) != expected_by_ext:
            print(f"    ERROR: Extension counts mismatch")
            test1_passed = False
            all_tests_passed = False
        else:
            print(f"    ✓ Extension counts correct")
        
        print(f"  - Lines by directory: Expected {expected_by_dir}, Got {dict(lines_by_directory)}")
        if dict(lines_by_directory) != expected_by_dir:
            print(f"    ERROR: Directory counts mismatch")
            test1_passed = False
            all_tests_passed = False
        else:
            print(f"    ✓ Directory counts correct")
        
        if test1_passed:
            print("\nTEST 1: PASSED")
        else:
            print("\nTEST 1: FAILED")
    
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            import shutil
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")
    
    # Test 2: Empty directory
    print("\n\nTEST 2: Empty directory")
    print("----------------------")
    
    test_dir = "loc_test_empty"
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)
    
    try:
        # Create empty test directory
        os.makedirs(test_dir)
        print(f"Created empty test directory: {test_dir}")
        
        # Count lines
        print("\nCounting lines in empty directory...")
        counter = LineCounter(extensions=[".py"], ignore_directories=[])
        total_lines, lines_by_extension, lines_by_directory = counter.count_lines_in_directory(test_dir)
        
        # Expected results
        expected_total = 0
        expected_by_ext = {}
        expected_by_dir = {}
        
        # Verify results
        test2_passed = True
        
        print("\nChecking results:")
        print(f"  - Total lines: Expected {expected_total}, Got {total_lines}")
        if total_lines != expected_total:
            print(f"    ERROR: Total line count should be 0 for empty directory")
            test2_passed = False
            all_tests_passed = False
        else:
            print(f"    ✓ Total count correct")
        
        print(f"  - Lines by extension: Expected {expected_by_ext}, Got {dict(lines_by_extension)}")
        if len(lines_by_extension) != 0:
            print(f"    ERROR: Extension counts should be empty")
            test2_passed = False
            all_tests_passed = False
        else:
            print(f"    ✓ Extension counts correct")
        
        print(f"  - Lines by directory: Expected {expected_by_dir}, Got {dict(lines_by_directory)}")
        if len(lines_by_directory) != 0:
            print(f"    ERROR: Directory counts should be empty")
            test2_passed = False
            all_tests_passed = False
        else:
            print(f"    ✓ Directory counts correct")
        
        if test2_passed:
            print("\nTEST 2: PASSED")
        else:
            print("\nTEST 2: FAILED")
    
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            import shutil
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")
    
    # Test 3: Directory with ignored subdirectories
    print("\n\nTEST 3: Directory with ignored subdirectories")
    print("-----------------------------------------")
    
    test_dir = "loc_test_ignore"
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)
    
    try:
        # Create test directory structure with ignored dirs
        os.makedirs(os.path.join(test_dir, "src"))
        os.makedirs(os.path.join(test_dir, "node_modules"))  # Should be ignored
        os.makedirs(os.path.join(test_dir, ".git"))  # Should be ignored
        
        # Create some test files
        test_files = [
            (os.path.join(test_dir, "src", "main.py"), "line1\nline2\nline3\n", 3),
            (os.path.join(test_dir, "node_modules", "ignored.py"), "line1\nline2\n", 2),  # Should be ignored
            (os.path.join(test_dir, ".git", "ignored.py"), "line1\nline2\n", 2)  # Should be ignored
        ]
        
        print("Creating test directory structure with ignored directories:")
        for file_path, content, line_count in test_files:
            with open(file_path, "w") as f:
                f.write(content)
            print(f"  - Created {file_path} with {line_count} lines")
        
        # Count lines
        print("\nCounting lines with ignore directories: ['node_modules', '.git']...")
        counter = LineCounter(extensions=[".py"], ignore_directories=["node_modules", ".git"])
        total_lines, lines_by_extension, lines_by_directory = counter.count_lines_in_directory(test_dir)
        
        # Expected results
        expected_total = 3  # Only the lines in src/main.py
        expected_by_ext = {".py": 3}
        expected_by_dir = {"src": 3}
        
        # Verify results
        test3_passed = True
        
        print("\nChecking results:")
        print(f"  - Total lines: Expected {expected_total}, Got {total_lines}")
        if total_lines != expected_total:
            print(f"    ERROR: Files in ignored directories should not be counted")
            test3_passed = False
            all_tests_passed = False
        else:
            print(f"    ✓ Total count correct (ignored directories not counted)")
        
        print(f"  - Lines by extension: Expected {expected_by_ext}, Got {dict(lines_by_extension)}")
        if dict(lines_by_extension) != expected_by_ext:
            print(f"    ERROR: Extension counts should not include ignored directories")
            test3_passed = False
            all_tests_passed = False
        else:
            print(f"    ✓ Extension counts correct")
        
        print(f"  - Lines by directory: Expected {expected_by_dir}, Got {dict(lines_by_directory)}")
        if dict(lines_by_directory) != expected_by_dir:
            print(f"    ERROR: Directory counts should not include ignored directories")
            test3_passed = False
            all_tests_passed = False
        else:
            print(f"    ✓ Directory counts correct")
        
        if test3_passed:
            print("\nTEST 3: PASSED")
        else:
            print("\nTEST 3: FAILED")
    
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            import shutil
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")
    
    # Summary
    print("\n======================")
    if all_tests_passed:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED!")
    print("======================")
    
    return all_tests_passed


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        main() 