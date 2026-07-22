from database.database import get_connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    connection.commit()
    connection.close()


def save_upload(filename, filepath):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO uploads (filename, filepath) VALUES (?, ?)",
        (filename, filepath)
    )

    connection.commit()
    connection.close()