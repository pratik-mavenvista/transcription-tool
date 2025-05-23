# Running Unit Tests

This document provides instructions on how to run the unit tests for the Flask application. The tests are written using Python's built-in `unittest` framework.

## Prerequisites

1.  **Python Environment**: Ensure you have Python 3 installed and a virtual environment set up for the project.
2.  **Dependencies**: Install the project dependencies, including testing-specific ones if any were added (though for `unittest` with Flask, usually the main app dependencies are sufficient).
    ```bash
    pip install -r requirements.txt 
    ```
    (Assuming you have a `requirements.txt` file. If not, ensure Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Werkzeug, etc., are installed.)

## Test Setup

The tests are configured to use an in-memory SQLite database (`sqlite:///:memory:`). This ensures that tests run quickly and do not interfere with your development database. The configuration `TestConfig` in `app/config.py` also disables CSRF protection for forms during testing to simplify test submissions.

The base test class (`tests/base_test.py:BaseTestCase`) handles:
*   Creating the Flask application with the test configuration.
*   Setting up an application context.
*   Creating all database tables before each test (`db.create_all()`).
*   Dropping all database tables after each test (`db.drop_all()`).
*   Providing a test client (`self.client`) for making requests to the application.
*   Helper methods for common actions like creating a test user and logging in/out.

## Running Tests

To run all unit tests, navigate to the root directory of the project (the directory containing the `app` and `tests` folders) in your terminal and execute the following command:

```bash
python -m unittest discover tests
```

This command will automatically discover all test files (matching `test_*.py`) within the `tests` directory and its subdirectories, and run all test methods (methods starting with `test_`) found within them.

**Verbose Output:**

For more detailed output, you can use the `-v` flag:

```bash
python -m unittest discover -v tests
```

## Interpreting Results

*   **`.` (dot)**: Indicates a test passed.
*   **`F`**: Indicates a test failed. The output will include a traceback and details about the failure.
*   **`E`**: Indicates an error occurred during a test (e.g., an unhandled exception in the test code itself or the application code it's testing). The output will include a traceback.
*   **`s`**: Indicates a test was skipped.

At the end of the test run, a summary will be displayed, showing the total number of tests run and the counts of passes, failures, errors, and skips.

## Example

If your project structure is:

```
your-flask-app/
├── app/
├── tests/
│   ├── __init__.py
│   ├── base_test.py
│   ├── test_auth.py
│   ├── test_models.py
│   ├── test_transcriptions.py
│   └── test_mom.py
├── run.py
└── TESTING.md
... (other files)
```

You would run the tests from the `your-flask-app/` directory.
