# Contributing to sigmap-pytools

Thank you for your interest in contributing to sigmap-pytools! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/WillHCode/Sigmap-PyTools.git
   cd Sigmap-PyTools
   ```
3. Install the package in editable mode:
   ```bash
   cd sigmap-pytools/
   pip install -e .
   pip install -r requirements_test.txt
   ```

## Development Workflow

1. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Ensure tests pass:
   ```bash
   cd sigmap-pytools/
   pytest -v
   ```
4. Commit your changes with clear messages
5. Push to your fork
6. Open a Pull Request

## Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

## Testing

- Write tests for new features
- Ensure all existing tests pass
- Aim for good test coverage
- Tests should be in the `sigmap-pytools/tests/` directory

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation if needed
3. Add a clear description of your changes
4. Reference any related issues
5. Ensure your branch is up to date with main

## Reporting Issues

When reporting issues, please include:

- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Python version and environment details
- Relevant error messages or tracebacks

## Feature Requests

For feature requests, please:

- Describe the feature clearly
- Explain the use case
- Discuss possible implementation approaches
- Consider backwards compatibility

## Questions?

Feel free to open a discussion on GitHub if you have questions about contributing.

Thank you for contributing to sigmap-pytools!

