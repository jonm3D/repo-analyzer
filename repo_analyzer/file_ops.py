import os


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
    with open(file_path, "r", errors="ignore") as infile:
        content = []
        for line in infile:
            if max_chars is not None and char_count + len(line) > max_chars:
                content.append(line[: max_chars - char_count])
                char_count = max_chars
                break
            else:
                content.append(line)
                char_count += len(line)
    return "".join(content), char_count


def read_config_file(config_path):
    """
    Read filenames from a configuration file.

    Parameters:
    config_path (str): Path to the configuration file.

    Returns:
    list: List of filenames read from the configuration file.
    """
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r") as file:
        filenames = [line.strip() for line in file if line.strip()]
    return filenames
