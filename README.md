# Repository Summarizer for LLMs

This tool combines the contents of a GitHub repository into a single text file, making it easier to use with Large Language Models (LLMs). It generates a summary of the project, including a directory tree and concatenated contents of specified files, with the option to prioritize a main file.

## Features

- **Repository Summarization**: Combines the contents of a GitHub repository into a single text file for easy use with LLMs.
- **Directory Tree Generation**: Provides a detailed directory tree structure of the repository.
- **File Concatenation**: Concatenates specified files into an output file in the order listed in the configuration file.
- **Main File Prioritization**: Prioritizes a specified main file in the output.
- **Hidden Files Inclusion**: Optionally includes hidden files and directories.
- **Pattern Matching**: Supports wildcard and regex entries for specifying file patterns.
- **Customization**: Allows customization of maximum characters, tree depth, and items per directory.

## Installation

To install the necessary dependencies, run:

```sh
pip install -r requirements.txt
```

## Usage

```sh
python main.py [directory] [-m MAIN_FILE] [-c MAX_CHARS] [-t TREE_DEPTH] [-i] [-x MAX_ITEMS] [-n INCLUDE]
```

### Arguments

- `directory` (str): The path to the local repository.
- `-m`, `--main_file` (str): The main file to prioritize in the output.
- `-c`, `--max_chars` (int): Maximum number of characters to include in the output file.
- `-t`, `--tree_depth` (int): Maximum depth of the directory tree to include in the output file.
- `-i`, `--include_hidden`: Include hidden files and directories.
- `-x`, `--max_items` (int): Maximum number of items to include in each directory to avoid clutter.
- `-n`, `--include` (str): Path to the configuration file with filename patterns to include in the output.

### Example

```sh
python main.py /path/to/repository -m main.py -c 10000 -t 5 -i -x 100 -n config.txt
```

## Configuration File

The configuration file should contain filename patterns to include in the output, one pattern per line. Wildcards and regex entries are supported.

Example `config.txt`:

```
*.py
*.md
*.json
```

## Example Output

To demonstrate the tool's functionality, we have run the tool on itself. You can find the generated summary [here](example.txt). 