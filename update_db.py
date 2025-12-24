import sqlite3
import os
import shutil

# Configuration
DB_PATH = 'instance/database.db'

# --- 1. Define Source and Destination Directories ---
# This matches the folder structure you showed in your screenshot
SOURCE_DIR = os.path.join('static', 'assets', 'images', 'delicacies')
DEST_DIR = os.path.join('static', 'uploads')

# Mapping Delicacy Names to Image Filenames
# These filenames MUST match what is inside your SOURCE_DIR
IMAGE_MAPPING = {
    "Kek Lapis Sarawak": "kek-lapis-sarawak.jpg",
    "Kuih Kaswi Pandan": "kuih-kaswi-pandan.jpg",
    "Kuih Ketayap": "kuih-ketayap.jpg",
    "Kuih Lapis": "kuih-lapis.jpg",
    "Kuih Seri Muka": "kuih-seri-muka.jpg",
    "Kuih Talam": "kuih-talam.png",
    # Note: .png based on your screenshot (assuming kuih-kalam.png is typo for talam)
    "Kuih Ubi Kayu": "kuih-ubi-kayu.jpg",
    "Onde Onde": "onde-onde.jpg"
}


def migrate_and_seed():
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: {DB_PATH} not found. Run app.py first to create it.")
        return

    # Ensure uploads directory exists
    os.makedirs(DEST_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- 🛠️ Starting Database Update ---")

    # 1. Check if 'image_filename' column exists
    cursor.execute("PRAGMA table_info(delicacy_info)")
    columns = [info[1] for info in cursor.fetchall()]

    if 'image_filename' not in columns:
        print("adding 'image_filename' column...")
        try:
            cursor.execute("ALTER TABLE delicacy_info ADD COLUMN image_filename VARCHAR(255)")
            print("✅ Column added successfully.")
        except Exception as e:
            print(f"⚠️ Error adding column: {e}")
    else:
        print("ℹ️ Column 'image_filename' already exists.")

    # 2. Update Data and Copy Images
    print("\n--- 🌱 Seeding Image Data & Copying Files ---")

    for name, filename in IMAGE_MAPPING.items():
        # A. Copy image from assets to uploads folder
        source_path = os.path.join(SOURCE_DIR, filename)
        dest_path = os.path.join(DEST_DIR, filename)

        if os.path.exists(source_path):
            try:
                shutil.copy(source_path, dest_path)
                print(f"   📂 Copied: {filename}")
            except Exception as e:
                print(f"   ⚠️ Copy Failed for {filename}: {e}")
        else:
            print(f"   ⚠️ Image Source Not Found: {source_path}")
            # We continue anyway to update the DB, assuming you might add the file later

        # B. Update Database Record
        cursor.execute("SELECT id FROM delicacy_info WHERE name = ?", (name,))
        row = cursor.fetchone()

        if row:
            try:
                cursor.execute("UPDATE delicacy_info SET image_filename = ? WHERE name = ?", (filename, name))
                print(f"   💾 DB Updated: {name} -> {filename}")
            except Exception as e:
                print(f"   ❌ DB Update Failed for {name}: {e}")
        else:
            print(f"   ⚠️ Skipped DB Update: {name} (Delicacy not found in DB)")

    conn.commit()
    conn.close()
    print("\n--- ✨ Database & File Update Complete ---")


if __name__ == "__main__":
    migrate_and_seed()