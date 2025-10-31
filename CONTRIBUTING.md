# Contributing to Slow Query Doctor

Thank you for your interest in contributing! 🎉

We welcome contributions of all kinds, including bug reports, feature requests, documentation improvements, and code changes.

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
   - Use a descriptive name, e.g. `feature/add-docker-support` or `bugfix/fix-log-parser`
3. **Make your changes**
   - Follow the code style and guidelines below
   - Add or update tests as appropriate
   - Test with multi-line, CSV, and JSON log files
4. **Commit your changes**
   - Use clear, descriptive commit messages
5. **Push to your fork**
6. **Open a Pull Request**
   - Describe your changes and reference any related issues
   - The PR will be reviewed and discussed before merging


## Code Style & Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style
- Use type hints where possible
- Write clear docstrings for all public functions and classes
- Use descriptive variable and function names
- Keep functions small and focused
- Add or update tests for new features and bug fixes
- Run `black` and `flake8` before submitting your PR
- Keep PRs focused and minimal; avoid unrelated changes
- Ensure you have `pyyaml`, `tqdm`, and all dev dependencies installed (see README)
- Reference `.slowquerydoctor.yml` for config-driven tests if needed

## Commit Messages

- Use the [Conventional Commits](https://www.conventionalcommits.org/) style when possible
- Example: `fix(parser): handle multiline queries in log parser`

## Pull Request Review Process

- All PRs are reviewed by maintainers
- Address requested changes promptly
- PRs must pass all CI checks before merging
- Large or breaking changes may require discussion or an issue first

## Reporting Bugs & Requesting Features

- Use [GitHub Issues](https://github.com/gmartinez-dbai/slow-query-doctor/issues)
- Provide as much detail as possible (logs, steps to reproduce, screenshots)
- Label your issue as `bug`, `feature`, or `question`

## Community Standards

- Be respectful and constructive
- No harassment, discrimination, or inappropriate behavior
- See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details

## Questions?

Open an issue or email gio@gmartinez.net

---

**Thank you for helping make Slow Query Doctor better!**
