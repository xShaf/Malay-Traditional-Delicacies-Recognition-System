import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import database as db
from io import BytesIO

# --- Configuration ---
app = Flask(__name__)
# The secret key is needed for flash messages
app.config['SECRET_KEY'] = 'a_very_secret_key_for_flash_messages'

# Set the folder for the ML recognition uploads (temporary storage)
ML_UPLOAD_FOLDER = 'static/temp_uploads'
# Define allowed file extensions (only images)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['ML_UPLOAD_FOLDER'] = ML_UPLOAD_FOLDER
# Ensure the upload directory exists
os.makedirs(ML_UPLOAD_FOLDER, exist_ok=True)


# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------
# --- Main Routes ---
# ---------------------

@app.route('/')
def index():
    """Renders the main page with the upload form."""
    page_title = "Malay Delicacies Recognition System"
    return render_template('index.html', title=page_title)


@app.route('/recognize', methods=['POST'])
def recognize_file():
    """
    Handles the file upload for ML recognition.
    Saves the file temporarily and redirects to results.
    """
    if 'file' not in request.files:
        flash('No file part in the request.', 'error')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        # 1. Sanitize the filename for security
        filename = secure_filename(file.filename)

        # 2. Save the file to the configured ML_UPLOAD_FOLDER
        file_path = os.path.join(app.config['ML_UPLOAD_FOLDER'], filename)

        # Use a BytesIO buffer to read the content first, then save.
        file_content = file.read()

        with open(file_path, 'wb') as f:
            f.write(file_content)

        # 3. --- Model Prediction Integration Point ---
        # result = your_prediction_function(file_path)

        # Redirect to a results page
        return redirect(url_for('show_result', filename=filename))

    flash('Invalid file type. Please upload a PNG, JPG, or JPEG image.', 'error')
    return redirect(url_for('index'))


@app.route('/result')
def show_result():
    """
    Renders the result page.
    (This is a placeholder for your model's output)
    """
    filename = request.args.get('filename')

    # Placeholder data - replace with your actual model output
    predicted_delicacy = "Kuih Lapis (Placeholder Result)"
    confidence = "98.5%"

    return render_template('result.html',
                           title="Prediction Result",
                           filename=filename,
                           delicacy=predicted_delicacy,
                           confidence=confidence)


# ---------------------
# --- Admin Routes ---
# ---------------------

@app.route('/add', methods=['GET', 'POST'])
def add_kuih_route():
    """
    Handles adding a new Kuih to the database, saving the image as PNG.
    This route now collects the 'recipe' field and passes it to the database function.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        history = request.form.get('history')
        # NEW: Collect the recipe data from the form
        recipe = request.form.get('recipe')
        image_file = request.files.get('image')

        # Basic validation
        # Ensure all required fields (name, history, recipe, image_file) are present
        if not all([name, history, recipe, image_file]):
            flash('All fields (Name, History, Recipe, Image) are required.', 'error')
            return redirect(request.url)

        if image_file.filename == '' or not allowed_file(image_file.filename):
            flash('Invalid or missing image file.', 'error')
            return redirect(request.url)

        # Use the updated database function to save the file as PNG and record path
        try:
            # Move the file pointer to the beginning for the database function to read it
            image_file.seek(0)

            # Pass the new 'recipe' parameter to db.add_kuih
            db.add_kuih(name, image_file, history, recipe)

            flash(f'Successfully added new Kuih: {name}!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'An error occurred while adding the Kuih: {e}', 'error')
            # Log the error for debugging
            app.logger.error(f"Error adding kuih: {e}")
            return redirect(request.url)

    # GET request: Show the add form
    return render_template('add_kuih.html', title="Add New Kuih")


# ---------------------
# --- App Run Block ---
# ---------------------

if __name__ == '__main__':
    with app.app_context():
        db.init_db()
        # Add a migration step to update the schema if the 'recipe' column is missing
        db.migrate_db()
    app.run(debug=True)