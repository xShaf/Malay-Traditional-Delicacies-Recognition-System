import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import database as db

# --- Configuration ---
app = Flask(__name__)

# Set the folder where uploaded images will be temporarily stored
UPLOAD_FOLDER = 'static/uploads'
# Define allowed file extensions (only images)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------


@app.route('/')
def index():
    """Renders the main page with the upload form."""
    page_title = "Malay Delicacies Recognition System"
    return render_template('index.html', title=page_title)


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles the file upload and initiates the prediction process."""
    if 'file' not in request.files:
        # Check if the file part is missing in the request
        return redirect(request.url)  # Redirect back to the index page

    file = request.files['file']

    if file.filename == '':
        # Check if no file was selected
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # 1. Sanitize the filename for security
        filename = secure_filename(file.filename)
        # 2. Save the file to the configured UPLOAD_FOLDER
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 3. --- Model Prediction Integration Point ---
        # At this point, you would load your trained model and run the prediction:
        # result = your_prediction_function(file_path)
        # For now, we'll just redirect to a results page with a placeholder filename

        # Redirect to a results page, passing the filename as a query parameter
        return redirect(url_for('show_result', filename=filename))

    # Handle cases where the file type is not allowed
    return 'Invalid file type', 400


@app.route('/result')
def show_result():
    """
    Renders the result page after the file has been uploaded.
    (This is a placeholder for your model's output)
    """
    filename = request.args.get('filename')

    # Placeholder prediction result
    # In a real app, this would be the actual output from your model
    predicted_delicacy = "Kuih Lapis (Placeholder Result)"
    confidence = "98.5%"

    return render_template('result.html',
                           title="Prediction Result",
                           filename=filename,
                           delicacy=predicted_delicacy,
                           confidence=confidence)


@app.route('/add', methods=['GET', 'POST'])
def add_kuih_route():
    if request.method == 'POST':
        name = request.form['name']
        history = request.form['history']
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            db.add_kuih(name, file_path, history)
            return redirect(url_for('index'))
    return render_template('add_kuih.html', title="Add Kuih")

if __name__ == '__main__':
    with app.app_context():
        db.init_db()
    app.run(debug=True)