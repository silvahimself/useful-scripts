import os
import sys
import concurrent.futures
import multiprocessing
import time
import threading
from collections import defaultdict

# ANSI color codes
YELLOW = "\033[33m"
CYAN = "\033[36m"
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

def handle_long_path(path):
    """Handle extremely long paths by using os.scandir instead of os.listdir"""
    try:
        # For Windows systems, try to use the extended-length path format
        if sys.platform == 'win32' and not path.startswith('\\\\?\\'):
            path = '\\\\?\\' + os.path.abspath(path)
        return path
    except Exception:
        return path

def get_file_size(fp):
    try:
        fp = handle_long_path(fp)
        return os.path.getsize(fp) if os.path.isfile(fp) else 0
    except (PermissionError, FileNotFoundError, OSError):
        return 0

def get_directory_size(path, progress_dict, lock):
    path = handle_long_path(path)
    total_size = 0
    file_list = []
    dir_list = []
    
    try:
        with lock:
            progress_dict[path] = {"status": "scanning", "message": "Scanning..."}
        
        with os.scandir(path) as scanner:
            for entry in scanner:
                try:
                    if entry.is_file():
                        file_list.append(entry.path)
                    elif entry.is_dir():
                        dir_list.append(entry.path)
                except OSError:
                    # Skip files/directories that cause OSError
                    continue
    except (PermissionError, OSError):
        with lock:
            progress_dict[path] = {"status": "error", "message": "Access Denied"}
        return 0
    
    # Process files in current directory
    total_files = len(file_list)
    files_processed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(32, len(file_list) or 1)) as executor:
        future_to_file = {executor.submit(get_file_size, fp): fp for fp in file_list}
        for future in concurrent.futures.as_completed(future_to_file):
            try:
                size = future.result()
                total_size += size
                files_processed += 1
                with lock:
                    progress_dict[path] = {"status": "scanning", "message": f"Scanning... ({files_processed}/{total_files} files)"}
            except Exception:
                # Skip files that cause exceptions
                files_processed += 1

    # Recursively process subdirectories
    for subdir in dir_list:
        try:
            subdir_size = get_directory_size(subdir, progress_dict, lock)
            total_size += subdir_size
        except (RecursionError, OSError):
            # Skip directories that cause recursion errors or OSErrors
            continue
    
    with lock:
        progress_dict[path] = {"status": "complete", "message": format_size(total_size)}
    
    return total_size

def format_size(size_in_bytes):
    if size_in_bytes is None:
        return "Access Denied"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

def colored_status(status_dict):
    if status_dict is None:
        return f"{YELLOW}Pending...{RESET}"
    
    status = status_dict.get("status", "pending")
    message = status_dict.get("message", "Pending...")
    
    if status == "pending":
        return f"{YELLOW}{message}{RESET}"
    elif status == "scanning":
        return f"{CYAN}{message}{RESET}"
    elif status == "complete":
        return f"{GREEN}{message}{RESET}"
    elif status == "error":
        return f"{RED}{message}{RESET}"
    return message

def display_progress(root_path, progress_dict):
    sys.stdout.write("\033c")  # Clear console
    print(f"Scanning: {root_path}")
    print("Size calculation in progress...\n")
    
    try:
        items = sorted(os.scandir(root_path), key=lambda x: x.name.lower())
        for item in items:
            if item.is_dir():
                status = progress_dict.get(item.path)
                colored_msg = colored_status(status)
                print(f"|- ({colored_msg}) {item.name}")
    except (PermissionError, OSError):
        print(f"{RED}Access Denied to root directory{RESET}")

def scan_directory(root_path):
    root_path = handle_long_path(root_path)
    sizes_dict = {}
    progress_dict = {}
    lock = threading.Lock()
    
    # Initialize all directories as pending
    try:
        with os.scandir(root_path) as scanner:
            for entry in scanner:
                if entry.is_dir():
                    with lock:
                        progress_dict[entry.path] = {"status": "pending", "message": "Pending..."}
    except (PermissionError, OSError):
        print(f"{RED}Error accessing the root directory{RESET}")
        return
    
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
    try:
        total_size = get_directory_size(root_path, progress_dict, lock)
        sizes_dict[root_path] = total_size
    except Exception as e:
        print(f"{RED}Error during scan: {str(e)}{RESET}")
        total_size = 0
    
    # Signal completion and show final results
    with lock:
        progress_dict['_scan_complete'] = True
    display_thread.join(timeout=1)
    
    # Display final results
    sys.stdout.write("\033c")
    print(f"Complete scan results for: {root_path}")
    print(f"Total size: {GREEN}{format_size(total_size)}{RESET}")
    
    try:
        items = sorted(os.scandir(root_path), key=lambda x: x.name.lower())
        for item in items:
            if item.is_dir():
                status = progress_dict.get(item.path)
                colored_msg = colored_status(status)
                print(f"|- ({colored_msg}) {item.name}")
    except (PermissionError, OSError):
        print(f"{RED}Access Denied to root directory{RESET}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        scan_path = sys.argv[1]
    else:
        scan_path = os.getcwd()
    
    scan_directory(scan_path)