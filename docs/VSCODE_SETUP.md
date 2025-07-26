# VS Code Setup Guide for KTMB Scraper

This guide will help you set up VS Code for optimal development experience with the KTMB Scraper project.

## 🚀 Quick Start

1. **Open the project in VS Code**:
   ```bash
   code ktmb-scraper
   ```

2. **Install recommended extensions**:
   - VS Code will prompt you to install recommended extensions
   - Or manually install: `Ctrl+Shift+P` → "Extensions: Install Extensions" → search for "Python"

3. **Select Python interpreter**:
   - `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Choose `.venv/bin/python` from the list

4. **Run tests**:
   - Open the Testing panel: `Ctrl+Shift+P` → "Testing: Focus on Test Explorer View"
   - Click the play button next to any test

## 📁 Project Structure

```
ktmb-scraper/
├── .vscode/                    # VS Code configuration
│   ├── settings.json          # Workspace settings
│   ├── launch.json            # Debug configurations
│   ├── tasks.json             # Build tasks
│   ├── extensions.json        # Recommended extensions
│   └── README.md              # This guide
├── tests/                     # Test files
│   ├── test_healthchecks.py   # HealthCheck tests
│   └── test_monitor_integration.py
├── notifications/             # Notification modules
├── scraper/                   # Main scraper code
├── utils/                     # Utility modules
└── examples/                  # Example scripts
```

## 🧪 Testing Features

### Test Explorer
- **View**: `Ctrl+Shift+P` → "Testing: Focus on Test Explorer View"
- **Run All**: Click the play button at the top of the Testing panel
- **Run Individual**: Click the play button next to any test
- **Debug Tests**: Set breakpoints and use the debug button

### Test Commands
- **Run All Tests**: `Ctrl+Shift+P` → "Python: Run All Tests"
- **Run Current Test File**: `Ctrl+Shift+P` → "Python: Run Current Test File"
- **Run Specific Test**: Right-click on test → "Run Test"

### Test Tasks
- **Run All Tests**: `Ctrl+Shift+P` → "Tasks: Run Task" → "Run All Tests"
- **Run HealthCheck Tests**: "Run HealthCheck Tests"
- **Run Monitor Integration Tests**: "Run Monitor Integration Tests"

## 🐛 Debugging

### Launch Configurations
1. **Python: Current File**: Run the currently open file
2. **Python: Run Tests**: Run all tests with debugging
3. **Python: Run Monitor**: Run the monitor script
4. **Python: Run Scraper**: Run the scraper module

### How to Debug
1. Set breakpoints by clicking in the gutter (left of line numbers)
2. Press `F5` or `Ctrl+Shift+P` → "Debug: Start Debugging"
3. Select the appropriate launch configuration
4. Use debug controls to step through code

## 🔧 Code Quality Tools

### Formatting
- **Black**: Automatic code formatting
- **Format on Save**: Automatically formats when you save (`Ctrl+S`)
- **Manual Format**: `Shift+Alt+F` or `Ctrl+Shift+P` → "Format Document"

### Import Sorting
- **isort**: Automatically sorts imports
- **Auto-sort**: Happens on save when format on save is enabled

### Linting
- **Flake8**: Real-time code quality checks
- **Problems Panel**: View all linting issues
- **Quick Fixes**: `Ctrl+.` to see available fixes

## ⌨️ Keyboard Shortcuts

### Testing
- `Ctrl+Shift+P` → "Testing: Focus on Test Explorer View"
- `Ctrl+Shift+P` → "Python: Run All Tests"
- `Ctrl+Shift+P` → "Python: Run Current Test File"

### Debugging
- `F5`: Start debugging
- `Ctrl+F5`: Run without debugging
- `F9`: Toggle breakpoint
- `F10`: Step over
- `F11`: Step into
- `Shift+F11`: Step out

### Code Quality
- `Shift+Alt+F`: Format document
- `Ctrl+Shift+P` → "Format Document"
- `Ctrl+.`: Quick fixes
- `F12`: Go to definition
- `Shift+F12`: Find all references

### General
- `Ctrl+Shift+P`: Command palette
- `Ctrl+P`: Quick open
- `Ctrl+Shift+F`: Find in files
- `Ctrl+Shift+E`: Explorer
- `Ctrl+Shift+G`: Source control

## 🛠️ Tasks

### Available Tasks
- **Run All Tests**: Run all test suites
- **Run HealthCheck Tests**: Run only healthcheck tests
- **Run Monitor Integration Tests**: Run monitor integration tests
- **Run Example**: Run the healthcheck example
- **Install Dependencies**: Install project dependencies with `uv sync`

### How to Run Tasks
1. `Ctrl+Shift+P` → "Tasks: Run Task"
2. Select the task you want to run
3. View output in the terminal

## 🔍 Troubleshooting

### Tests Not Discovered
- Ensure you're in the correct workspace folder
- Check that Python interpreter is set to `.venv/bin/python`
- Verify test files follow the pattern `test_*.py`
- Try reloading the window: `Ctrl+Shift+P` → "Developer: Reload Window"

### Import Errors
- Make sure virtual environment is activated
- Check that `PYTHONPATH` includes workspace root
- Verify all dependencies are installed: `uv sync`

### Formatting Not Working
- Ensure Black is installed: `uv add --dev black`
- Check Python extension is installed and enabled
- Verify "Format on Save" is enabled in settings
- Try manual format: `Shift+Alt+F`

### Debugging Issues
- Check launch configuration settings
- Ensure breakpoints are set correctly
- Verify Python interpreter is correct
- Check console output for errors

## 📦 Dependencies

### Development Dependencies
The project uses `uv` for dependency management. Development dependencies include:
- `black`: Code formatting
- `flake8`: Linting
- `isort`: Import sorting

### Installing Dependencies
```bash
# Install all dependencies
uv sync

# Install development dependencies
uv add --dev black flake8 isort
```

## 🎯 Best Practices

### Testing
- Write tests for new features
- Run tests before committing
- Use descriptive test names
- Group related tests in test classes

### Code Quality
- Format code before committing
- Fix linting issues
- Use type hints where appropriate
- Follow PEP 8 style guidelines

### Debugging
- Set breakpoints strategically
- Use logging for debugging
- Test edge cases
- Document complex logic

## 📚 Additional Resources

- [VS Code Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Python Testing in VS Code](https://code.visualstudio.com/docs/python/testing)
- [Debugging Python in VS Code](https://code.visualstudio.com/docs/python/debugging)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)

## 🤝 Contributing

When contributing to the project:
1. Ensure all tests pass
2. Format code with Black
3. Fix any linting issues
4. Add tests for new functionality
5. Update documentation as needed

---

Happy coding! 🚀 