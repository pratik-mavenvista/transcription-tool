# Flask Transcription and MoM Application

This is a Flask web application that provides user authentication, real-time audio transcription, and generation of Minutes of Meeting (MoM) from these transcriptions.

## Features

*   User registration, login, and logout.
*   Password reset (placeholder functionality).
*   Real-time audio transcription using the Web Speech API.
*   Saving transcriptions to a user-specific dashboard.
*   Generation and editing of Minutes of Meeting (MoM) from saved transcriptions.
*   Basic summarization for initial MoM content.

## Project Structure

```
your-flask-app/
├── app/                  # Main application package
│   ├── __init__.py       # Application factory, initializes Flask extensions
│   ├── auth.py           # Authentication routes (login, register, etc.)
│   ├── main.py           # Main application routes (index, transcribe, dashboard, MoM)
│   ├── models.py         # SQLAlchemy database models (User, Transcription, MoM)
│   ├── forms.py          # WTForms definitions
│   ├── utils.py          # Utility functions (e.g., basic summarizer)
│   ├── static/           # Static files (CSS, JS - if any beyond client-side JS in templates)
│   └── templates/        # HTML templates (Jinja2)
├── tests/                # Unit tests
│   ├── __init__.py
│   ├── base_test.py
│   ├── test_auth.py
│   ├── test_models.py
│   ├── test_transcriptions.py
│   └── test_mom.py
├── venv/                 # Virtual environment (example, should be in .gitignore)
├── run.py                # Script to run the Flask application and initialize DB
├── config.py             # Configuration classes (development, testing, production)
├── requirements.txt      # Python package dependencies
├── .gitignore            # Files and directories to be ignored by Git
├── DEPLOYMENT_GUIDE.md   # Guide for deploying the application
├── REVIEW_AND_FIXES.md   # Details of code review, fixes, and further recommendations
└── TESTING.md            # Instructions for running unit tests
```

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd your-flask-app
    ```

2.  **Create and Activate a Virtual Environment:**
    *   **Importance:** It is strongly recommended to use a virtual environment to isolate project dependencies and avoid conflicts with system-wide packages.
    ```bash
    python3 -m venv venv  # Or python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies:**
    *   Ensure your virtual environment is activated.
    *   The `requirements.txt` file contains all packages picked up during development. For production, this file should be pruned. See the "Deployment" section below and `DEPLOYMENT_GUIDE.md` / `REVIEW_AND_FIXES.md`.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**
    *   The application uses `app/config.py` for configuration.
    *   Essential configurations like `SECRET_KEY` and `SQLALCHEMY_DATABASE_URI` are defined there.
    *   For production, sensitive values should be set using environment variables. The `Config` class is designed to read from `os.environ`.

5.  **Database Initialization:**
    *   The application uses Flask-SQLAlchemy for database operations.
    *   Running the application with `python run.py` will automatically create the database tables (defined in `app/models.py`) if they don't already exist. This is handled by `db.create_all()` within the application context in `run.py`.

6.  **Running the Application:**
    *   With the virtual environment activated and dependencies installed:
    ```bash
    python run.py
    ```
    *   The application will typically be available at `http://127.0.0.1:5000/`.
    *   For development, you can also use the `flask` CLI (ensure `FLASK_APP=run.py` and `FLASK_DEBUG=1` are set as environment variables):
        ```bash
        export FLASK_APP=run.py
        export FLASK_DEBUG=1 # Enables debug mode and auto-reloader
        flask run
        ```

## Usage

*   Navigate to the application in your web browser.
*   Register a new user account or log in if you have an existing account.
*   Access the "Transcribe" page to use the real-time audio transcription feature.
*   Saved transcriptions will appear on your "Dashboard".
*   From the dashboard, you can generate or manage Minutes of Meeting (MoM) for each transcription.

## Testing

Refer to `TESTING.md` for detailed instructions on how to run the unit tests.

## Deployment

For deploying this application to a production environment, please refer to the comprehensive `DEPLOYMENT_GUIDE.md`. Key considerations include:

*   Using a production-ready WSGI server (e.g., Gunicorn, uWSGI).
*   Disabling debug mode.
*   Managing configurations and secrets securely using environment variables.
*   Setting up a robust production database.
*   **`requirements.txt`:** The `requirements.txt` file included in this repository was generated during development and may contain development-specific dependencies. **It is crucial to prune this file for production to include only necessary runtime packages.** Detailed instructions on how to create a production-ready `requirements.txt` can be found in `REVIEW_AND_FIXES.md` and are also mentioned in `DEPLOYMENT_GUIDE.md`.

## Further Information

*   `REVIEW_AND_FIXES.md`: Contains details about code reviews, fixes applied (like the open redirect vulnerability), and further recommendations for improvement (e.g., CSRF for AJAX, enhancing the summarizer).
*   `DEPLOYMENT_GUIDE.md`: Provides information on various deployment platforms and general best practices for deploying Flask applications.
*   `TESTING.md`: Instructions on running the provided unit tests.

This application serves as a demonstration of building a Flask application with various features.
Remember to review security configurations and best practices before deploying any application to a public server.
```
