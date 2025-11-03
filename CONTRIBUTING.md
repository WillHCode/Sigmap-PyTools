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
3. Open a Pull Request using our [pull request template](.github/pull_request_template.md)
4. Fill out all relevant sections in the PR template
5. Reference any related issues
6. Ensure your branch is up to date with main

## Reporting Issues

We use issue templates to help gather all necessary information. When reporting bugs:

- Use our [bug report template](https://github.com/WillHCode/Sigmap-PyTools/issues/new?template=bug_report.md)
- Include a clear description of the problem
- Provide steps to reproduce the issue
- Include expected vs actual behavior
- Specify Python version and environment details
- Include relevant error messages or tracebacks

## Feature Requests

We welcome feature requests! To suggest a new feature:

- Use our [feature request template](https://github.com/WillHCode/Sigmap-PyTools/issues/new?template=feature_request.md)
- Describe the feature clearly
- Explain the use case and benefits
- Discuss possible implementation approaches
- Consider backwards compatibility

## Security Issues

If you discover a security vulnerability, please **do not** open a public issue. Instead, please refer to our [Security Policy](.github/SECURITY.md) for instructions on how to report security issues responsibly.

## Questions?

Feel free to open a discussion on GitHub if you have questions about contributing.

Thank you for contributing to sigmap-pytools!

