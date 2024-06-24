import os
import argparse
import re
from concurrent.futures import ThreadPoolExecutor

def generate_tree(directory, depth=3, current_depth=0, max_items=50, include_hidden=False):
    """
    Generate a tree structure of the directory up to a specified depth.

    Parameters:
    directory (str): The root directory to start generating the tree from.
    depth (int): The maximum depth of the directory tree to include.
    current_depth (int): The current depth in the directory tree (used for recursion).
    max_items (int): Maximum number of items to include in each directory to avoid clutter.
    include_hidden (bool): Whether to include hidden files and directories.

    Returns:
    list: A list of strings representing the directory tree.
    """
    tree = []
    with os.scandir(directory) as entries:
        items = [entry.name for entry in entries if include_hidden or not entry.name.startswith('.')]
    items.sort()
    if len(items) > max_items:
        items = items[:max_items]
        items.append('...')  # Indicate that there are more items
    for item in items:
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            tree.append(f"{'  ' * current_depth}|-- {item}/")
            if current_depth < depth - 1:
                tree.extend(generate_tree(item_path, depth, current_depth + 1, max_items, include_hidden))
        else:
            tree.append(f"{'  ' * current_depth}|-- {item}")
    return tree

def read_file(file_path, max_chars, char_count):
    """
    Read a file up to a maximum number of characters.

    Parameters:
    file_path (str): The path to the file.
    max_chars (int): The maximum number of characters to read from the file.
    char_count (int): The current character count.

    Returns:
    tuple: A tuple containing the file content and the new character count.
    """
    with open(file_path, 'r', errors='ignore') as infile:
        content = []
        for line in infile:
            if max_chars is not None and char_count + len(line) > max_chars:
                content.append(line[:max_chars - char_count])
                char_count = max_chars
                break
            else:
                content.append(line)
                char_count += len(line)
    return ''.join(content), char_count

def extract_function_calls(file_path):
    """
    Extract function calls from a MATLAB file.

    Parameters:
    file_path (str): The path to the MATLAB file.

    Returns:
    set: A set of function names called in the file.
    """
    function_calls = set()
    with open(file_path, 'r', errors='ignore') as infile:
        for line in infile:
            matches = re.findall(r'\b(\w+)\s*\(', line)
            function_calls.update(matches)
    return function_calls

def find_all_dependencies(directory, main_file, extensions, include_hidden):
    """
    Find all dependent MATLAB functions called by the main file.

    Parameters:
    directory (str): The root directory to start searching for files.
    main_file (str): Path to the main MATLAB file.
    extensions (tuple): A tuple of file extensions to include.
    include_hidden (bool): Whether to include hidden files.

    Returns:
    set: A set of file paths for all dependent MATLAB functions.
    """
    dependencies = set()
    queue = [main_file]
    visited = set()

    while queue:
        current_file = queue.pop()
        if current_file in visited:
            continue
        visited.add(current_file)
        dependencies.add(current_file)
        function_calls = extract_function_calls(current_file)
        for root, _, files in os.walk(directory):
            if not include_hidden:
                files = [file for file in files if not file.startswith('.')]
            for file in files:
                if file.endswith(extensions) and file.replace('.m', '') in function_calls:
                    file_path = os.path.join(root, file)
                    if file_path not in visited:
                        queue.append(file_path)

    return dependencies

def concatenate_files(directory, output_file, extensions, max_chars, include_hidden=False, main_file=None):
    """
    Concatenate contents of specified file types into an output file.

    Parameters:
    directory (str): The root directory to start searching for files.
    output_file (str): The path of the output file to write concatenated contents.
    extensions (tuple): A tuple of file extensions to include.
    max_chars (int): The maximum number of characters to include in the output file.
    include_hidden (bool): Whether to include hidden files.
    main_file (str): Path to the main file to prioritize in the output.
    """
    char_count = 0
    dependencies = set()
    if main_file and main_file.endswith('.m'):
        dependencies = find_all_dependencies(directory, main_file, extensions, include_hidden)

    with open(output_file, 'a') as outfile:
        if main_file:
            outfile.write(f"\n\n--- {main_file} (Main File) ---\n\n")
            content, char_count = read_file(main_file, max_chars, char_count)
            outfile.write(content)
        
        with ThreadPoolExecutor() as executor:
            futures = []
            for root, _, files in os.walk(directory):
                if not include_hidden:
                    files = [file for file in files if not file.startswith('.')]
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path == main_file or (main_file and file_path not in dependencies):
                        continue
                    if file.endswith(extensions):
                        futures.append(executor.submit(read_file, file_path, max_chars, char_count))
            for future in futures:
                content, char_count = future.result()
                if content:
                    outfile.write(f"\n\n--- {file_path} ---\n\n")
                    outfile.write(content)
                if max_chars is not None and char_count >= max_chars:
                    print(f"Reached maximum character limit: {max_chars}")
                    return
    print(f"Files concatenated successfully, total characters: {char_count}")

def main():
    """
    Main function to parse arguments, generate directory tree, and concatenate files.
    """
    parser = argparse.ArgumentParser(description="Analyze the structure and specific file types of a local repository.")
    parser.add_argument("directory", type=str, help="The path to the local repository")
    parser.add_argument("--main_file", type=str, help="The main file to prioritize in the output")
    parser.add_argument("--max_chars", type=int, default=None, help="Maximum number of characters to include in the output file")
    parser.add_argument("--tree_depth", type=int, default=10, help="Maximum depth of the directory tree to include in the output file")
    parser.add_argument("--include_hidden", action='store_true', help="Include hidden files and directories")
    parser.add_argument("--max_items", type=int, default=50, help="Maximum number of items to include in each directory to avoid clutter")
    
    args = parser.parse_args()

    directory = args.directory
    main_file = args.main_file
    max_chars = args.max_chars
    tree_depth = args.tree_depth
    include_hidden = args.include_hidden
    max_items = args.max_items

    project_name = os.path.basename(os.path.abspath(directory))
    header = f"""
**Project Analysis Instructions**

Below is a summary of the project **{project_name}**, starting with the directory tree structure to provide an overview. This is followed by the main file, if specified, which serves as the primary runner for this tool. Use this main file to inform your understanding of all subsequent scripts, as it orchestrates the execution flow and primary logic of the project. Additional scripts have also been included for a comprehensive analysis of the tool.

Please perform the following tasks:

1. **Summarize the Tool/Code Purpose**: Provide a high-level summary of what this tool or code is designed to do.
2. **Identify and Summarize Critical Functions and Dependencies**: Note any critical functions, methods, or dependencies within the project. Summarize their roles and how they interact with the main file.
3. **Contextual Analysis**: Use the main file to contextualize the functionality and importance of the subsequent scripts. Highlight how they contribute to the overall operation of the tool.

*Prompt Engineering Instructions*:
- **Contextual Understanding**: Maintain the context of the main file when analyzing subsequent scripts to ensure coherence in the overall project understanding.
- **Focus on Dependencies**: Pay special attention to dependencies between files and how they influence the execution flow.
- **Execution Flow**: Clearly outline the execution flow starting from the main file to other dependent scripts.
- **Avoid Redundancy**: Do not reproduce the code verbatim. Instead, focus on storing and utilizing the code structure and logic in your memory for this analysis.
"""

    output_file = os.path.join(directory, os.path.basename(directory) + "_summary.txt")
    
    print(f"Generating directory tree for {directory}...")
    tree = generate_tree(directory, depth=tree_depth, max_items=max_items, include_hidden=include_hidden)
    
    with open(output_file, 'w') as outfile:
        outfile.write(header)
        outfile.write("Directory Structure:\n")
        outfile.write("\n".join(tree))
        outfile.write("\n\nConcatenated Files:\n")

    print(f"Concatenating files for {directory}...")
    concatenate_files(directory, output_file, ('.py', '.m', '.r', '.ipynb', '.html', '.md', '.txt'), max_chars, include_hidden=include_hidden, main_file=main_file)

    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
