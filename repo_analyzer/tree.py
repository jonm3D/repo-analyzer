import os

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
