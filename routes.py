import os
import time
import logging
import numpy as np
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import func
from tensorflow.keras.models import load_model

from models import db, User, InferenceLog, Feedback, DelicacyInfo
from utils import (
    MODEL_PATHS, CLASS_NAMES, DISPLAY_NAMES, SYSTEM_STATE,
    prepare_image, load_model_metrics
)

# Create a Blueprint
main = Blueprint('main', __name__)


@main.route('/')
def landing():
    total = InferenceLog.query.count()
    avg_val = db.session.query(func.avg(InferenceLog.confidence_score)).scalar()
    avg_acc = round(avg_val * 100, 1) if avg_val else 0.0
    return render_template('landing.html', avg_accuracy=avg_acc)


@main.route('/library')
def library():
    all_delicacies = DelicacyInfo.query.all()
    all_delicacies.sort(key=lambda x: x.name)
    return render_template('library.html', delicacies=all_delicacies)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            logging.info(f"Login: {username} (Admin: {user.is_admin})")
            return redirect(url_for('main.admin_dashboard') if user.is_admin else url_for('main.recognize'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username taken', 'error')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registered! Login now.', 'success')
            return redirect(url_for('main.login'))
    return render_template('register.html')


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.landing'))


# --- ADMIN ROUTES ---
@main.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('is_admin'): return redirect(url_for('main.login'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'start_system':
            selected_name = request.form.get('model_select')
            if selected_name in MODEL_PATHS:
                try:
                    path = os.path.join(current_app.config['MODEL_FOLDER'], MODEL_PATHS[selected_name])
                    logging.info(f"Loading {path}...")
                    SYSTEM_STATE['loaded_model'] = load_model(path)
                    SYSTEM_STATE['is_active'] = True
                    SYSTEM_STATE['current_model_name'] = selected_name
                    flash(f'Started with {selected_name}', 'success')
                except Exception as e:
                    logging.error(f"Load Error: {e}")
                    flash(f"Error loading model: {e}", 'error')
        elif action == 'stop_system':
            SYSTEM_STATE['is_active'] = False
            SYSTEM_STATE['loaded_model'] = None
            flash('System Stopped', 'warning')

    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of logs per page

    # Use .paginate() instead of .limit().all()
    pagination = InferenceLog.query.order_by(InferenceLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    logs = pagination.items  # Get the list of logs for current page

    # Other Data
    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).limit(20).all()
    delicacies = DelicacyInfo.query.all()
    total_inferences = InferenceLog.query.count()

    # Avg Accuracy Calculation
    avg_val = db.session.query(func.avg(InferenceLog.confidence_score)).scalar()
    avg_accuracy = round(avg_val * 100, 1) if avg_val else 0.0

    # Graph Data
    usage_data = db.session.query(InferenceLog.model_used, func.count(InferenceLog.id)).group_by(
        InferenceLog.model_used).all()
    graph_labels = [d[0] for d in usage_data] if usage_data else ['No Data']
    graph_values = [d[1] for d in usage_data] if usage_data else [0]

    return render_template('dashboard.html',
                           state=SYSTEM_STATE,
                           logs=logs,
                           pagination=pagination,  # Pass pagination object
                           feedbacks=feedbacks,
                           delicacies=delicacies,
                           avg_accuracy=avg_accuracy,
                           total_inferences=total_inferences,
                           graph_labels=graph_labels,
                           graph_values=graph_values,
                           available_models=MODEL_PATHS.keys())

# --- CRUD ROUTES ---
@main.route('/admin/delicacy/add', methods=['POST'])
def add_delicacy():
    if not session.get('is_admin'): return redirect(url_for('main.login'))
    name = request.form.get('name')
    if DelicacyInfo.query.filter_by(name=name).first():
        flash('Exists already!', 'error')
    else:
        file = request.files.get('delicacy_image')
        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        new_d = DelicacyInfo(
            name=name,
            description=request.form.get('description'),
            history=request.form.get('history'),
            ingredients=request.form.get('ingredients'),
            recipe=request.form.get('recipe'),
            image_filename=filename
        )
        db.session.add(new_d)
        db.session.commit()
        flash('Added!', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/delicacy/edit/<int:id>', methods=['POST'])
def edit_delicacy(id):
    if not session.get('is_admin'): return redirect(url_for('main.login'))
    d = DelicacyInfo.query.get_or_404(id)

    file = request.files.get('delicacy_image')
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        d.image_filename = filename

    d.name = request.form.get('name')
    d.description = request.form.get('description')
    d.history = request.form.get('history')
    d.ingredients = request.form.get('ingredients')
    d.recipe = request.form.get('recipe')

    db.session.commit()
    flash('Updated!', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/delicacy/delete/<int:id>', methods=['POST'])
def delete_delicacy(id):
    if not session.get('is_admin'): return redirect(url_for('main.login'))
    d = DelicacyInfo.query.get_or_404(id)
    db.session.delete(d)
    db.session.commit()
    flash('Deleted!', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/get_logs')
def get_logs():
    if not session.get('is_admin'): return "Access Denied", 403
    try:
        with open('system.log', 'r') as f:
            return "".join(f.readlines()[-100:])
    except:
        return "No logs."


@main.route('/admin/evaluation')
def admin_evaluation():
    if not session.get('is_admin'): return redirect(url_for('main.login'))
    current_metrics = load_model_metrics(current_app.root_path)
    if not current_metrics:
        flash("No evaluation data found. Please upload model_metrics.json.", "warning")
    models = list(current_metrics.keys())
    accuracies = [m.get('accuracy', 0) for m in current_metrics.values()]
    losses = [m.get('loss', 0) for m in current_metrics.values()]
    return render_template('evaluation.html', metrics=current_metrics, chart_labels=models, chart_accuracies=accuracies, chart_losses=losses)


@main.route('/admin/graph/<path:filename>')
def get_graph(filename):
    if not session.get('is_admin'): return "Access Denied", 403
    directory = os.path.join(current_app.root_path, 'MyModels', 'graphs')
    from flask import send_from_directory
    return send_from_directory(directory, filename)


# --- RECOGNITION ---
@main.route('/recognize', methods=['GET', 'POST'])
def recognize():
    if not SYSTEM_STATE['is_active']: return render_template('unavailable.html')

    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            try:
                start = time.time()
                img_arr = prepare_image(path, SYSTEM_STATE['current_model_name'])
                preds = SYSTEM_STATE['loaded_model'].predict(img_arr)
                idx = np.argmax(preds[0])
                conf = float(preds[0][idx])

                raw_name = CLASS_NAMES[idx]
                display_name = DISPLAY_NAMES.get(raw_name, raw_name)
                time_ms = round((time.time() - start) * 1000, 2)

                logging.info(f"Result: {display_name} ({conf:.2f})")

                log_entry = InferenceLog(
                    filename=filename, model_used=SYSTEM_STATE['current_model_name'],
                    predicted_class=display_name, confidence_score=conf,
                    inference_time_ms=time_ms, user_id=session.get('user_id')
                )
                db.session.add(log_entry)
                db.session.commit()

                session['last_result'] = {
                    "class": display_name,
                    "confidence": f"{conf * 100:.1f}%",
                    "time": f"{time_ms} ms",
                    "image": filename
                }
                return redirect(url_for('main.show_result'))

            except Exception as e:
                logging.error(f"Inference Fail: {e}")
                flash("Analysis Failed. Check logs.", "error")
                return redirect(url_for('main.recognize'))

    return render_template('recognize.html')


@main.route('/result')
def show_result():
    result = session.get('last_result')
    if not result:
        return redirect(url_for('main.recognize'))
    info = DelicacyInfo.query.filter_by(name=result['class']).first()
    if not info:
        info = DelicacyInfo(name=result['class'], description="Info loading...", history="", ingredients="", recipe="")
    return render_template('result.html', result=result, info=info)


@main.route('/feedback', methods=['POST'])
def submit_feedback():
    if not session.get('user_id'): return redirect(url_for('main.login'))
    fb = Feedback(user_id=session['user_id'], rating=request.form.get('rating'), comment=request.form.get('comment'))
    db.session.add(fb)
    db.session.commit()
    flash('Feedback Sent!', 'success')
    return redirect(url_for('main.recognize'))