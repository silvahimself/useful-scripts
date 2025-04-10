#!/usr/bin/env python3

import os
import sys
from collections import defaultdict

class LineCounter:
    def __init__(self, extensions, ignore_directories):
        self.extensions = extensions
        self.ignore_directories = ignore_directories

    def count_lines_in_directory(self, directory_path):
        if not directory_path or not isinstance(directory_path, str):
            raise ValueError("Directory path cannot be null or empty")
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory '{directory_path}' not found")
        
        lines_by_extension = defaultdict(int)
        total_lines = self._count_lines(directory_path, lines_by_extension)
        
        return total_lines, lines_by_extension
    
    def _count_lines(self, directory_path, lines_by_extension, line_count=0):
        count = line_count
        
        try:
            # Count lines in files
            for file_name in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file_name)
                
                # Process files
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file_path)
                    if ext in self.extensions:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = [line for line in f.read().splitlines() if line.strip()]
                                lines_in_file = len(lines)
                                count += lines_in_file
                                lines_by_extension[ext] += lines_in_file
                        except Exception:
                            # Skip files that can't be read
                            continue
                
                # Process subdirectories
                elif os.path.isdir(file_path):
                    dir_name = os.path.basename(file_path)
                    if dir_name in self.ignore_directories or dir_name.startswith('.'):
                        continue
                    
                    count = self._count_lines(file_path, lines_by_extension, count)
        
        except Exception:
            # Skip directories that can't be processed
            pass
        
        return count

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
        total_lines, lines_by_extension = counter.count_lines_in_directory(target_dir)
        
        print(f"Total lines of code: {total_lines}")
        print("\nBreakdown by file type:")
        
        # Sort extensions by line count (descending)
        for ext, count in sorted(lines_by_extension.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ext}: {count} lines")
    
    except Exception as ex:
        print(f"Error: {str(ex)}")

if __name__ == "__main__":
    main() 