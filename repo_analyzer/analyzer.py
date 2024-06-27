import os
import argparse
import time
import fnmatch
from .file_ops import read_file, read_config_file
from .tree import generate_tree

def find_files_by_config(directory, patterns, include_hidden, valid_extensions):
    """
    Find and return a list of text and code files in the directory matching the patterns from the config file.

    Parameters:
    directory (str): The root directory to start searching for files.
    patterns (list): List of filename patterns to include in the output.
    include_hidden (bool): Whether to include hidden files.
    valid_extensions (set): Set of valid file extensions to include.

    Returns:
    list: List of full paths to files that match the criteria.
    """
    files_to_include = []
    for root, _, files in os.walk(directory):
        if not include_hidden:
            files = [file for file in files if not file.startswith('.')]
        for file in files:
            if not patterns or any(fnmatch.fnmatch(os.path.join(root, file), os.path.join(directory, pattern)) for pattern in patterns):
                if os.path.splitext(file)[1] in valid_extensions:
                    files_to_include.append(os.path.join(root, file))

    # Sort files_to_include according to the order in patterns
    sorted_files = []
    for pattern in patterns:
        for file_path in files_to_include:
            if fnmatch.fnmatch(file_path, os.path.join(directory, pattern)):
                sorted_files.append(file_path)
    
    # Reverse the order to match the order specified by the user in the config file
    if patterns:
        sorted_files.reverse()
    else:
        sorted_files = files_to_include

    return sorted_files

def concatenate_files(files_to_include, output_file, max_chars, main_file=None):
    """
    Concatenate contents of specified files into an output file.

    Parameters:
    files_to_include (list): List of file paths to include.
    output_file (str): The path of the output file to write concatenated contents.
    max_chars (int): The maximum number of characters to include in the output file.
    main_file (str): Path to the main file to prioritize in the output.
    """
    char_count = 0
    if os.path.exists(output_file):
        files_to_include = [f for f in files_to_include if f != output_file]

    with open(output_file, 'a') as outfile:
        if main_file and main_file in files_to_include:
            outfile.write(f"\n\n--- {main_file} (Main File) ---\n\n")
            content, char_count = read_file(main_file, max_chars, char_count)
            outfile.write(content)
            files_to_include.remove(main_file)

        for file_path in files_to_include:
            start_time = time.time()
            print(f"Processing file: {file_path}")
            content, char_count = read_file(file_path, max_chars, char_count)
            elapsed_time = time.time() - start_time

            if elapsed_time > 10:
                print(f"Skipping file {file_path} (took too long: {elapsed_time:.2f} seconds)")
                continue

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
    parser.add_argument("-m", "--main_file", type=str, help="The main file to prioritize in the output")
    parser.add_argument("-c", "--max_chars", type=int, default=None, help="Maximum number of characters to include in the output file")
    parser.add_argument("-t", "--tree_depth", type=int, default=10, help="Maximum depth of the directory tree to include in the output file")
    parser.add_argument("-i", "--include_hidden", action='store_true', help="Include hidden files and directories")
    parser.add_argument("-x", "--max_items", type=int, default=50, help="Maximum number of items to include in each directory to avoid clutter")
    parser.add_argument("-n", "--include", type=str, help="Path to the configuration file with filename patterns to include in the output")

    args = parser.parse_args()

    directory = os.path.abspath(args.directory)
    main_file = args.main_file
    max_chars = args.max_chars
    tree_depth = args.tree_depth
    include_hidden = args.include_hidden
    max_items = args.max_items
    config_file = args.include

    valid_extensions = {'.txt', '.py', '.md', '.json', '.xml', '.html', '.css', '.js', '.java', '.cpp', '.c', '.hpp', '.h', '.m', 'ipynb'}

    if config_file:
        config_file = os.path.abspath(config_file)
        patterns = read_config_file(config_file)
        if patterns is None or not patterns or all(name.isspace() for name in patterns):
            print(f"Configuration file {config_file} not found, is empty, or only contains spaces.")
            patterns = []
    else:
        patterns = []

    project_name = os.path.basename(directory)
    header = f"""
**Project Analysis Instructions**

Below is a summary of the project **{project_name}**, starting with the directory tree structure to provide an overview. This is followed by the main file, if specified, which serves as the primary runner for this tool. Use this main file to inform your understanding of all subsequent scripts, as it orchestrates the execution flow and primary logic of the project. Additional scripts have also been included for a comprehensive analysis of the tool.

User-specified files to include:
{', '.join(patterns) if patterns else 'None'}

Please perform the following tasks:

1. **Summarize the Tool/Code Purpose**: Provide a high-level summary of what this tool or code is designed to do.
2. **Identify and Summarize Critical Functions and Dependencies**: Note any critical functions, methods, or dependencies within the project. Summarize their roles and how they interact with the main file.
3. **Contextual Analysis**: Use the main file to contextualize the functionality and importance of the subsequent scripts. Highlight how they contribute to the overall operation of the tool.

*Prompt Engineering Instructions*:
- **Core Function Focus**: Prioritize analysis on core functions, such as scientific computations, large computations, or scripts that manage multiple functions. Avoid spending time on wrapper functions or utility functions unless they play a significant role.
- **Execution Flow**: Clearly outline the execution flow starting from the main file to other dependent scripts.
- **File Boundaries**: Recognize the start of a new file with the pattern --- <file_path> ---.
- **Avoid Redundancy**: Do not reproduce the code verbatim. Instead, focus on storing and utilizing the code structure and logic in your memory for this analysis.

"""

    output_file = os.path.join(directory, project_name + "_summary.txt")
    
    print(f"Generating directory tree for {directory}...")
    tree = generate_tree(directory, depth=tree_depth, max_items=max_items, include_hidden=include_hidden)
    
    with open(output_file, 'w') as outfile:
        outfile.write(header)
        outfile.write("Directory Structure:\n")
        outfile.write("\n".join(tree))
        outfile.write("\n\nConcatenated Files:\n")

    print(f"Finding files to concatenate in {directory}...")
    files_to_include = find_files_by_config(directory, patterns, include_hidden, valid_extensions)

    if not files_to_include:
        print("No files found to include based on the configuration.")

    print(f"Concatenating files for {directory}...")
    concatenate_files(files_to_include, output_file, max_chars, main_file=main_file)

    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
