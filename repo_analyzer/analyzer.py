import os
import argparse
from .file_ops import read_file, read_config_file
from .tree import generate_tree

def find_files(directory, filenames, include_hidden):
    """
    Find and return a list of files in the directory matching the filenames.

    Parameters:
    directory (str): The root directory to start searching for files.
    filenames (list): List of filenames to include in the output.
    include_hidden (bool): Whether to include hidden files.

    Returns:
    list: List of full paths to files that match the criteria.
    """
    files_to_include = []
    for root, _, files in os.walk(directory):
        if not include_hidden:
            files = [file for file in files if not file.startswith('.')]
        for file in files:
            if file in filenames:
                files_to_include.append(os.path.join(root, file))
    return files_to_include

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
            content, char_count = read_file(file_path, max_chars, char_count)
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
    parser.add_argument("--config_file", type=str, default="files_to_include.txt", help="Path to the configuration file with filenames to include in the output")

    args = parser.parse_args()

    directory = args.directory
    main_file = args.main_file
    max_chars = args.max_chars
    tree_depth = args.tree_depth
    include_hidden = args.include_hidden
    max_items = args.max_items
    config_file = args.config_file

    filenames = read_config_file(config_file)

    project_name = os.path.basename(os.path.abspath(directory))
    header = f"""
**Project Analysis Instructions**

Below is a summary of the project **{project_name}**, starting with the directory tree structure to provide an overview. This is followed by the main file, if specified, which serves as the primary runner for this tool. Use this main file to inform your understanding of all subsequent scripts, as it orchestrates the execution flow and primary logic of the project. Additional scripts have also been included for a comprehensive analysis of the tool.

User-specified files to include:
{', '.join(filenames) if filenames else 'None'}

Please perform the following tasks:

1. **Summarize the Tool/Code Purpose**: Provide a high-level summary of what this tool or code is designed to do.
2. **Identify and Summarize Critical Functions and Dependencies**: Note any critical functions, methods, or dependencies within the project. Summarize their roles and how they interact with the main file.
3. **Contextual Analysis**: Use the main file to contextualize the functionality and importance of the subsequent scripts. Highlight how they contribute to the overall operation of the tool.

*Prompt Engineering Instructions*:
- **Core Function Focus**: Prioritize analysis on core functions, such as scientific computations, large computations, or scripts that manage multiple functions. Avoid spending time on wrapper functions or utility functions unless they play a significant role.
- **Execution Flow**: Clearly outline the execution flow starting from the main file to other dependent scripts.
- **File Boundaries**: Recognize the start of a new file with the pattern `--- <file_path> ---`.
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

    print(f"Finding files to concatenate in {directory}...")
    files_to_include = find_files(directory, filenames, include_hidden)

    print(f"Concatenating files for {directory}...")
    concatenate_files(files_to_include, output_file, max_chars, main_file=main_file)

    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
