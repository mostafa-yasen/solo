# Solo Project

## Project Overview

Solo is a modular Python web application designed to manage users and projects efficiently. The project leverages a clean architecture with separate modules for users and projects, making it easy to extend and maintain. It uses a database backend (SQLite by default) and includes migration support for evolving the schema over time.

## Features
- User management (registration, authentication, etc.)
- Project management (CRUD operations)
- RESTful API endpoints for users and projects
- Database migrations using Alembic
- Modular code structure for scalability

## Technology Stack
- Python 3.12+
- Flask (or FastAPI, depending on implementation)
- SQLite (default, can be replaced)
- Alembic for migrations

## Getting Started
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd solo
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run database migrations:
   ```bash
   alembic upgrade head
   ```
4. Start the application:
   ```bash
   python app.py
   ```

## Folder Structure
- `users/` - User models and routes
- `projects/` - Project models and routes
- `migrations/` - Database migration scripts
- `app.py` - Main application entry point

## Contributing
Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## License
This project is licensed under the MIT License.
