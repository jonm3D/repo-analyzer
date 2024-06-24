Project: Repository Analyzer

Description:
The Repository Analyzer is a tool designed to analyze the structure and specific file types of a local repository. It generates a summary of the project, including a directory tree and concatenated contents of specified file types, highlighting the main file if specified.

Features:
- Generate a directory tree up to a specified depth.
- Concatenate contents of specified file types into a single output file.
- Prioritize and highlight a main file for better contextual analysis.
- Include dependencies of the main MATLAB file by analyzing function calls.

Usage:
1. Clone or download the repository to your local machine.
2. Ensure you have Python installed on your machine.
3. Install the necessary Python packages using the command:
   pip install -r requirements.txt

Running the Script:
To run the Repository Analyzer, use the following command format:

repo-analyzer <directory> [options]

Options:
- directory: The path to the local repository to be analyzed.
- --main_file: The main file to prioritize in the output (e.g., main.m).
- --max_chars: Maximum number of characters to include in the output file.
- --tree_depth: Maximum depth of the directory tree to include in the output file.
- --include_hidden: Include hidden files and directories (use as a flag).
- --max_items: Maximum number of items to include in each directory to avoid clutter.

Example:
repo-analyzer /path/to/local/repo --main_file /path/to/local/repo/main.m --max_chars 10000 --tree_depth 5 --include_hidden --max_items 50

Output:
The script generates an output file in the specified directory with the name <directory>_summary.txt. The output file includes:
- A directory tree structure.
- Contents of the main file, if specified.
- Concatenated contents of other specified file types.

Project Structure:
- repo_analyzer/
  - __init__.py
  - cli.py
- README.txt (this file)
- requirements.txt
