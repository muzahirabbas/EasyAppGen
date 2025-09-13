import os
import sys

# A set of common language names or file types to skip after a path declaration.
LANG_SPECIFIERS_TO_SKIP = {
    "python", "javascript", "js", "typescript", "ts", "html", "css", "json",
    "yaml", "yml", "dockerfile", "text", "txt", "shell", "bash", "sh"
}

def extract_file_path(line: str) -> str | None:
    """
    Checks if a line is a file path declaration and returns the clean path if it is.
    """
    stripped_line = line.strip()
    if stripped_line.startswith("// File: "):
        return stripped_line.split(": ", 1)[1]
    return None

def save_file(root_dir: str, relative_path: str, content: list):
    """A helper function to save a file, prepending the root directory to its path."""
    full_path = os.path.join(root_dir, relative_path) if root_dir else relative_path
    
    parent_dir = os.path.dirname(full_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    
    with open(full_path, "w", encoding="utf-8") as out:
        out.writelines(content)
    print(f"[+] Created {full_path}")

def build_from_txt(input_file: str):
    current_file = None
    content = []
    root_dir = None
    is_new_file = False # **CHANGE**: A new flag to track the state

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            if not root_dir and stripped and stripped.endswith('/') and ' ' not in stripped:
                root_dir = stripped.rstrip('/')
                print(f"✅ Project root folder identified: {root_dir}")
                continue
            
            if stripped.startswith(('├──', '└──', '│')):
                continue

            path = extract_file_path(line)

            if path:
                if current_file and content:
                    save_file(root_dir, current_file, content)

                current_file = path
                content = []
                is_new_file = True # **CHANGE**: Set the flag when a new file is found
                continue

            if current_file:
                # **THE NEW, MORE ROBUST FIX IS HERE**
                if is_new_file:
                    if not stripped: # 1. Skip any blank lines at the start of a file block
                        continue
                    
                    # 2. Check if the first non-blank line is a specifier
                    if stripped.lower() in LANG_SPECIFIERS_TO_SKIP:
                        is_new_file = False # Reset the flag
                        continue # Skip the specifier line
                    
                    # 3. If it's not a specifier, it's real code. Reset flag and fall through to append it.
                    is_new_file = False

                # This part now only runs after the initial header/specifier has been handled
                if "This is a binary file" in line:
                    full_binary_path = os.path.join(root_dir, current_file) if root_dir else current_file
                    parent_dir = os.path.dirname(full_binary_path)
                    if parent_dir:
                        os.makedirs(parent_dir, exist_ok=True)
                        
                    if not os.path.exists(full_binary_path):
                        open(full_binary_path, "wb").close()
                    print(f"[!] Placeholder created for binary: {full_binary_path}")
                    
                    current_file = None
                    content = []
                else:
                    content.append(line)

    if current_file and content:
        save_file(root_dir, current_file, content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python builder.py <ai_output.txt>")
        sys.exit(1)

    input_txt = sys.argv[1]
    build_from_txt(input_txt)
    print("\n✅ Project structure built successfully.")