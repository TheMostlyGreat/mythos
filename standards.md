# Pythonic Code: Best Practices and Guidelines

## 1. Follow the Zen of Python
The Zen of Python provides guiding principles for writing Python code. Access it by typing `import this` in a Python shell. Key principles include:
- Beautiful is better than ugly.
- Explicit is better than implicit.
- Simple is better than complex.
- Readability counts.

## 2. Code Formatting

### 2.1 PEP 8 Style Guide
Adhere to PEP 8 for consistent and readable code:
- **Indentation**: Use 4 spaces per indentation level.
- **Line Length**: Limit lines to 79 characters.
- **Blank Lines**: Separate top-level functions and class definitions with two blank lines. Use a single blank line to separate methods inside a class.
- **Imports**: Place imports on separate lines and group them in the following order: standard library imports, related third-party imports, and local application/library-specific imports. Use absolute imports over relative imports.

### 2.2 Naming Conventions
- **Variables and Functions**: Use `snake_case`.
- **Classes**: Use `CamelCase`.
- **Constants**: Use `UPPERCASE` with underscores.

## 3. Writing Readable Code

### 3.1 Comments
- **Block Comments**: Use block comments to explain code. Each line starts with `#` and a space.
- **Inline Comments**: Use inline comments sparingly. Place them at least two spaces from the statement.
- **Documentation Strings (Docstrings)**: Use docstrings for all public modules, functions, classes, and methods.

### 3.2 Descriptive Naming
- Use descriptive names for variables, functions, and classes.

## 4. Best Practices for Writing Functions

### 4.1 Function Length
- Keep functions small and focused on a single task.

### 4.2 Function Arguments
- Limit the number of arguments to a maximum of 5.

### 4.3 Avoid Side Effects
- Avoid modifying global state or arguments within functions.

## 5. Object-Oriented Design

### 5.1 Class Design
- Each class should represent a single concept or entity. Prefer composition over inheritance for flexibility.

### 5.2 Encapsulation
- Use a single underscore `_` to indicate internal use for class variables and methods.

## 6. Error Handling

### 6.1 Using Exceptions
- Use exceptions for error handling, and provide meaningful error messages.

### 6.2 Creating Custom Exceptions
- Create custom exception classes for specific error conditions.

## 7. Code Optimization

### 7.1 Avoid Premature Optimization
- Write clear and correct code first, then optimize.

### 7.2 Efficient Data Structures
- Use appropriate data structures (e.g., lists for ordered collections, dictionaries for key-value pairs).

### 7.3 List Comprehensions
- Use list comprehensions for concise and efficient list creation.

## 8. Testing

### 8.1 Write Tests
- Write unit tests for your code using frameworks like `unittest` or `pytest`.

### 8.2 Test Coverage
- Aim for high test coverage, focusing on critical and complex code.

### 8.3 Continuous Integration
- Use continuous integration tools to run tests on every code change.

## 9. Documentation

### 9.1 Docstrings
- Write comprehensive docstrings for modules, classes, and functions.

### 9.2 API Documentation
- Use tools like Sphinx to generate API documentation from your docstrings.

## 10. Code Reviews

## 12. Performance Considerations

### 12.1 Profiling
- Use profiling tools to identify performance bottlenecks.

### 12.2 Memory Management
- Be mindful of memory usage, especially with large data sets. Use generators for large data streams.

## 13. Security Practices

### 13.1 Input Validation
- Always validate and sanitize user inputs.

### 13.2 Secure Coding
- Follow secure coding practices to prevent vulnerabilities.

## 16. Pythonic Code Principles

### 16.1 Use Python’s Built-in Functions and Libraries
```python
# Instead of this:
squares = []
for x in range(10):
    squares.append(x**2)

# Do this:
squares = [x**2 for x in range(10)]
```

### 16.2 Use List Comprehensions and Generator Expressions
```python
# List comprehension
squares = [x**2 for x in range(10)]

# Generator expression
squares_gen = (x**2 for x in range(10))
```

### 16.3 Use Enumerate Instead of Range
```python
# Instead of this:
for i in range(len(my_list)):
    print(i, my_list[i])

# Do this:
for index, value in enumerate(my_list):
    print(index, value)
```

### 16.4 Use `with` for Resource Management
```python
# Instead of this:
file = open("file.txt", "r")
try:
    data = file.read()
finally:
    file.close()

# Do this:
with open("file.txt", "r") as file:
    data = file.read()
```

### 16.5 Handle Exceptions Properly
```python
# Instead of this:
try:
    risky_operation()
except:
    handle_error()

# Do this:
try:
    risky_operation()
except SpecificException as e:
    handle_error(e)
```

### 16.6 Use `f-strings` for String Formatting
```python
# Instead of this:
name = "Alice"
greeting = "Hello, %s!" % name

# Or this:
greeting = "Hello, {}".format(name)

# Do this:
greeting = f"Hello, {name}!"
```

### 16.7 Write Functions with Single Responsibility
- Each function should do one thing well.

### 16.8 Use `dataclasses` for Simple Classes
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```

### 16.9 Prefer `is` for Comparing to `None`
```python
# Instead of this:
if value == None:
    ...

# Do this:
if value is None:
    ...
```

### 16.10 Simplify Conditions
```python
# Instead of this:
if len(my_list) > 0:
    ...

# Do this:
if my_list:
    ...
```

## 17. Comprehensive Docstring Template

### Template
```python
def function_name(param1, param2):
    """
    Brief summary of the function (one line).

    Extended description of the function, explaining its purpose, behavior, and
    any important details. Include any context or background information that 
    might help the user understand how the function works.

    Parameters
    ----------
    param1 : type
        Description of the first parameter.
    param2 : type
        Description of the second parameter.

    Returns
    -------
    return_type
        Description of the return value. If there are multiple return values,
        describe each one on a new line.

    Raises
    ------
    ExceptionType
        Description of the exception raised, if applicable. List each exception
        on a new line with a brief explanation.

    Examples
    --------
    Examples of how to use the function, preferably using doctest format for
    executable examples.

    >>> result = function_name(param1, param2)
    >>> print(result)
    """
    pass
```

### Example
```python
def add_numbers(a, b):
    """
    Adds two numbers and returns the result.

    This function takes two numeric arguments and returns their sum. It supports
    both integers and floating-point numbers. The function raises a TypeError if
    either of the inputs is not a number.

    Parameters
    ----------
    a : int or float
        The first number to add.
    b : int or float
        The second number to add.

    Returns
    -------
    int or float
        The sum of the two numbers. The return type matches the input types.

    Raises
    ------
    TypeError
        If either of the inputs is not a number.

    Examples
    --------
    Adding two integers:

    >>> add_numbers(1, 2)
    3

    Adding two floating-point numbers:

    >>> add_numbers(1.5, 2.5)
    4.0

    Adding an integer and a floating-point number:

    >>>