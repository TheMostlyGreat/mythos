import os

def trace(func):
    def wrapper(*args, **kwargs):
        print(f"Calling function: {func.__name__} with arguments: {args} and keyword arguments: {kwargs}")
        result = func(*args, **kwargs)
        print(f"Function {func.__name__} returned: {result}")
        return result
    return wrapper

def ensure_unique_directory(path: str) -> str:
    """Ensure that a unique directory exists at the specified path.

    Args:
        path (str): The path where the directory should be created.

    Returns:
        str: The path of the created unique directory.
    """
    if not os.path.exists(path):
        path = create_unique_directory(path)  # Call the existing function to create the directory

    return path

def create_unique_directory(path: str) -> str:
    """Create a unique directory at the specified path by appending a counter if necessary.

    Args:
        path (str): The path where the directory should be created.

    Returns:
        str: The path of the created unique directory.
    """
    base_path = path  # Store the base path
    counter = 1  # Initialize counter for uniqueness
    while os.path.exists(path):
        # Append '-counter' to the base path to create a new directory name
        path = f"{base_path}-{counter}"  
        counter += 1  # Increment counter for next iteration
    os.makedirs(path, exist_ok=True)  # Create the unique directory

    return path

def get_unique_filename(path: str, filename: str, extension: str = ".md") -> str:
    """Generate a unique filename by appending a counter if necessary.

    Args:
        path (str): The directory path where the file will be created.
        filename (str): The base name of the file.
        extension (str): The file extension (default is '.md').

    Returns:
        str: A unique filename that does not already exist in the specified path.
    """
    base_filename = f"{path}/{filename}"  # Base filename without extension
    filename = base_filename + extension  # Initial filename with extension
    counter = 1  # Initialize counter for uniqueness
    while os.path.exists(filename):
        # If the filename already exists, create a new filename
        # Append '-counter' before the extension to ensure uniqueness
        filename = f"{base_filename}-{counter}{extension}"  # Create new filename
        counter += 1  # Increment counter for next iteration
        
    return filename  # Return the unique filename

def create_unique_file(content: str, path: str, filename: str, extension: str = ".md") -> str:
    """Create a unique file with the specified content.

    Args:
        content (str): The content to write to the file.
        path (str): The directory path where the file will be created.
        filename (str): The base name of the file.
        extension (str): The file extension (default is '.md').

    Returns:
        str: The path of the created unique file.
    """
    ensure_unique_directory(path)

    unique_filename = get_unique_filename(path, filename, extension)
    
    # Save the file with the unique filename
    with open(unique_filename, 'w') as file:
        file.write(content)  # Create an empty file

    return unique_filename


