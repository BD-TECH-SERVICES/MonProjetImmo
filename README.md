# MonProjetImmo

This project uses Django and Wagtail. The easiest way to run it is with Docker, which also provides a PostgreSQL database.

## Quick start with Docker

1. Install Docker and Docker Compose.
2. Copy `.env.example` to `.env` and adjust values if needed.
3. Run `docker-compose up --build`.

The application will be available at `http://localhost:9000`.

## Manual setup

1. Install Python 3.10+ and PostgreSQL.
2. Create a virtual environment and install the dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```
3. Create a PostgreSQL database and user matching the values in your `.env` file.
4. Apply migrations and start the development server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

Environment variables are read from a `.env` file if present, making it easy to configure the database host, user and password.
