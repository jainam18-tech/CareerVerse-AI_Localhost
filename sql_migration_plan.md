# SQL Migration Plan: CareerVerse

This document outlines the proposed SQL schema and migration steps to move CareerVerse from a mock session-based system to a persistent MySQL database.

## 1. Database Schema

### Table: `users`
| Column | Type | Constraints |
| :--- | :--- | :--- |
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT |
| `username` | VARCHAR(80) | NOT NULL |
| `email` | VARCHAR(120) | UNIQUE, NOT NULL |
| `password_hash` | VARCHAR(255) | NOT NULL |
| `is_verified` | BOOLEAN | DEFAULT FALSE |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### Table: `login_history`
| Column | Type | Constraints |
| :--- | :--- | :--- |
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT |
| `user_id` | INT | FOREIGN KEY (users.id) |
| `login_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### Table: `user_performance`
| Column | Type | Constraints |
| :--- | :--- | :--- |
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT |
| `user_id` | INT | FOREIGN KEY (users.id) |
| `marks_json` | TEXT | NOT NULL (JSON data) |
| `performance_level` | VARCHAR(100) | e.g., 'SSC', 'HSC Science' |

### Table: `chat_messages`
| Column | Type | Constraints |
| :--- | :--- | :--- |
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT |
| `user_id` | INT | FOREIGN KEY (users.id) |
| `role` | VARCHAR(10) | 'user' or 'ai' |
| `content` | TEXT | NOT NULL |
| `timestamp` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

## 2. Implementation Steps

1. **Prerequisites**:
   - Install `flask-sqlalchemy` and `pymysql`.
   - Setup a MySQL database named `careerverse`.

2. **Configuration**:
   - Update `config.py` with `SQLALCHEMY_DATABASE_URI`.
   - Add database credentials to `.env`.

3. **Backend Updates**:
   - Initialize `db = SQLAlchemy(app)` in `app.py`.
   - Define model classes matching the schema above.
   - Replace all usages of the global `USERS` dictionary with `db.session` queries (e.g., `User.query.filter_by(email=email).first()`).
   - Update `/signup` to hash passwords and save `User` objects.
   - Update `/login` to check hashes and track `LoginHistory`.

4. **Verification**:
   - Run a migration script or use `db.create_all()` within the app context.
   - Test user registration and login flows.
