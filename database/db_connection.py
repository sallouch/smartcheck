import sqlite3
import os
# Database setup

db_path ="smartcheck.db"
def get_connection():
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")# enforce foreign keys
    return conn


def ensure_schema():
    """Create the database and tables from schema.sql if needed."""
    conn = get_connection()
    cursor = conn.cursor()
    if os.path.exists("schema.sql"):
        with open("schema.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
    else:
        raise FileNotFoundError("schema.sql not found in project folder")
    conn.commit()
    conn.close()#Closes the connection to the database
