import sqlite3
import os
from PIL import Image
from io import BytesIO

# --- Configuration ---
DATABASE_NAME = 'kuih.db'
# Directory where image files will be stored
UPLOAD_FOLDER = 'static/kuih_images'

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ----------------- Database Functions -----------------

def get_db(db_name=DATABASE_NAME):
    conn = sqlite3.connect(db_name)
    return conn


def init_db(db_name=DATABASE_NAME):
    conn = get_db(db_name)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS kuih (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image TEXT NOT NULL,
            history TEXT NOT NULL,
            recipe TEXT NOT NULL  -- NEW COLUMN ADDED HERE
        )
    ''')
    conn.commit()
    conn.close()


def migrate_db(db_name=DATABASE_NAME):
    """Adds the new 'recipe' column if it doesn't exist."""
    conn = get_db(db_name)
    c = conn.cursor()
    try:
        # Check if the column exists by trying to add it
        c.execute("ALTER TABLE kuih ADD COLUMN recipe TEXT")
        conn.commit()
        print("Database migrated successfully: 'recipe' column added.")
    except sqlite3.OperationalError as e:
        # This error typically means the column already exists
        if 'duplicate column name' in str(e):
            print("Database schema is already up to date.")
        else:
            print(f"Migration error: {e}")
    finally:
        conn.close()


def get_all_kuih(db_name=DATABASE_NAME):
    """Retrieves all kuih from the database."""
    conn = get_db(db_name)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM kuih")
    kuih_list = c.fetchall()
    conn.close()
    return kuih_list


def add_kuih(name, image_file, history, recipe, db_name=DATABASE_NAME):
    """
    Saves the image file as PNG and records the file path in the database.

    :param name: The name of the kuih.
    :param image_file: The uploaded file object (e.g., from Flask's request.files['image']).
    :param history: The history/description of the kuih.
    :param recipe: The recipe of the kuih. <--- NEW PARAMETER
    """

    # 1. Generate a unique filename and define the path
    safe_name = "".join(c if c.isalnum() else "_" for c in name.lower())

    conn = get_db(db_name)
    c = conn.cursor()
    c.execute("SELECT MAX(id) FROM kuih")
    next_id = (c.fetchone()[0] or 0) + 1

    image_filename = f"{safe_name}_{next_id}.png"
    image_path = os.path.join(UPLOAD_FOLDER, image_filename)

    try:
        # 2. Open and convert the image to PNG using PIL
        img = Image.open(BytesIO(image_file.read()))
        img.save(image_path, format='PNG')
        db_image_path = os.path.join(UPLOAD_FOLDER, image_filename).replace('\\', '/')

    except Exception as e:
        print(f"Error saving image: {e}")
        raise

    # 3. Insert the record into the database (Note: recipe added to the tuple)
    try:
        c.execute("INSERT INTO kuih (name, image, history, recipe) VALUES (?, ?, ?, ?)",
                  (name, db_image_path, history, recipe))  # <--- UPDATED TUPLE
        conn.commit()
    except Exception as e:
        print(f"Error inserting into DB: {e}")
        if os.path.exists(image_path):
            os.remove(image_path)
        raise
    finally:
        conn.close()