import os

def generate_tree(directory, depth=3, current_depth=0):
    tree = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            tree.append(f"{'  ' * current_depth}|-- {item}/")
            if current_depth < depth - 1:
                tree.extend(generate_tree(item_path, depth, current_depth + 1))
        else:
            tree.append(f"{'  ' * current_depth}|-- {item}")
    return tree

def concatenate_files(directory, output_file, extensions):
    with open(output_file, 'a') as outfile:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(extensions):
                    file_path = os.path.join(root, file)
                    outfile.write(f"\n\n--- {file_path} ---\n\n")
                    with open(file_path, 'r', errors='ignore') as infile:
                        outfile.write(infile.read())

def main(directory):
    output_file = os.path.join(directory, "repo_structure_and_files.txt")
    tree = generate_tree(directory)
    
    with open(output_file, 'w') as outfile:
        outfile.write("Directory Structure:\n")
        outfile.write("\n".join(tree))
        outfile.write("\n\nConcatenated Files:\n")

    concatenate_files(directory, output_file, ('.py', '.mat', '.txt', '.md'))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a tree structure and concatenate specific file types.")
    parser.add_argument("directory", type=str, help="The top-level directory of the repository")
    
    args = parser.parse_args()
    main(args.directory)
