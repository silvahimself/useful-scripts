import os
import sys
import concurrent.futures
import multiprocessing
import time
import threading
from collections import defaultdict

def get_file_size(fp):
    try:
        return os.path.getsize(fp) if os.path.isfile(fp) else 0
    except (PermissionError, FileNotFoundError):
        return 0

def get_directory_size(path, progress_dict, lock):
    total_size = 0
    file_list = []
    dir_list = []
    
    try:
        with os.scandir(path) as scanner:
            for entry in scanner:
                if entry.is_file():
                    file_list.append(entry.path)
                elif entry.is_dir():
                    dir_list.append(entry.path)
    except PermissionError:
        return None
    
    # Process files in current directory
    total_files = len(file_list)
    files_processed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(32, len(file_list) or 1)) as executor:
        future_to_file = {executor.submit(get_file_size, fp): fp for fp in file_list}
        for future in concurrent.futures.as_completed(future_to_file):
            size = future.result()
            total_size += size
            files_processed += 1
            with lock:
                progress_dict[path] = f"Scanning... ({files_processed}/{total_files} files)"

    # Recursively process subdirectories
    for subdir in dir_list:
        subdir_size = get_directory_size(subdir, progress_dict, lock)
        if subdir_size is not None:
            total_size += subdir_size
    
    with lock:
        progress_dict[path] = format_size(total_size)
    return total_size

def format_size(size_in_bytes):
    if size_in_bytes is None:
        return "Access Denied"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

def display_progress(root_path, progress_dict):
    sys.stdout.write("\033c")  # Clear console
    print(f"Scanning: {root_path}")
    print("Size calculation in progress...\n")
    
    try:
        items = sorted(os.scandir(root_path), key=lambda x: x.name.lower())
        for item in items:
            if item.is_dir():
                status = progress_dict.get(item.path, "Pending...")
                print(f"|- ({status}) {item.name}")
    except PermissionError:
        print("Access Denied to root directory")

def scan_directory(root_path):
    sizes_dict = {}
    progress_dict = {}
    lock = threading.Lock()
    
    def update_display():
        while True:
            with lock:
                if '_scan_complete' in progress_dict:
                    break
                display_progress(root_path, progress_dict)
            time.sleep(0.5)
    
    # Start display update thread
    display_thread = threading.Thread(target=update_display)
    display_thread.daemon = True
    display_thread.start()
    
    # Perform the scan
    total_size = get_directory_size(root_path, progress_dict, lock)
    sizes_dict[root_path] = total_size
    
    # Signal completion and show final results
    with lock:
        progress_dict['_scan_complete'] = True
    display_thread.join(timeout=1)
    
    # Display final results
    sys.stdout.write("\033c")
    print(f"Complete scan results for: {root_path}")
    print(f"Total size: {format_size(total_size)}\n")
    
    try:
        items = sorted(os.scandir(root_path), key=lambda x: x.name.lower())
        for item in items:
            if item.is_dir():
                status = progress_dict.get(item.path, "Access Denied")
                print(f"|- ({status}) {item.name}")
    except PermissionError:
        print("Access Denied to root directory")

if __name__ == "__main__":
    current_directory = os.getcwd()
    scan_directory(current_directory)