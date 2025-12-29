# Malay Traditional Delicacies Recognition System 🧁

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange)
![Flask](https://img.shields.io/badge/Flask-Web%20App-green)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-Corporate%20Theme-06b6d4)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A state-of-the-art AI-powered web application designed to preserve and promote Malay Traditional Delicacies heritage. This system utilizes advanced Deep Learning models to accurately identify 7 distinct types of traditional Malay delicacies from images.

## 🌟 Key Features

*   **🔍 Instant Recognition**: Upload an image to identify delicacies with high accuracy.
*   **📚 Heritage Library**: A searchable database containing recipes, history, and ingredients for each delicacy.
*   **📊 Admin Dashboard**: Real-time system monitoring, model switching, and inference logging.
*   **📈 Performance Evaluation**: Built-in comprehensive metrics and graphs (Confusion Matrix, Loss/Accuracy Curves) for all trained models.
*   **📱 Responsive & Professional UI**: Designed with a "Corporate Heritage" theme using **TailwindCSS** and **DaisyUI**, fully responsive for mobile and desktop.

## 🧠 Deep Learning Models

The core of the system consists of Convolutional Neural Networks (CNNs) trained on a custom dataset of **~7,000 images**. We experimented with training from scratch (AlexNet) and Transfer Learning (ResNet50, MobileNetV2, EfficientNetB0).

### Dataset Classes (7 Types)
1.  **Kuih Kaswi Pandan**
2.  **Kuih Ketayap**
3.  **Kuih Lapis**
4.  **Kuih Seri Muka**
5.  **Kuih Talam**
6.  **Kuih Ubi Kayu**
7.  **Onde-Onde**

### Model Performance Comparison
Models were evaluated on a dedicated test set (10% split). **ResNet50 (Fine-Tuned)** achieved the state-of-the-art performance.

| Model Name | Accuracy | Precision | Recall | F1-Score | Loss |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **ResNet50_FT** 🏆 | **96.41%** | **96.45%** | **96.41%** | **96.41%** | **0.1089** |
| MobileNetV2_FT | 94.48% | 94.70% | 94.48% | 94.53% | 0.1810 |
| EfficientNetB0 | 93.78% | 93.81% | 93.78% | 93.78% | 0.1606 |
| ResNet50 | 91.57% | 91.81% | 91.57% | 91.47% | 0.2366 |
| MobileNetV2 | 91.30% | 91.51% | 91.30% | 91.27% | 0.2442 |
| AlexNet (Scratch) | 73.62% | 77.39% | 73.62% | 73.32% | 0.7476 |

## 📂 Data Preparation & Workflow

The model training process (detailed in `Malay_Traditional_Delicacies_Recognition_System.ipynb`) utilizes **Google Colab** and **Google Drive** for efficient data management and training.

### 1. Data Source & Storage
*   **Google Drive Integration**: The dataset is stored on Google Drive (`/content/drive/MyDrive/FYP`) to persist data across Colab sessions.
*   **Directory Structure**:
    *   `train/`: Initially contains the master dataset of raw images organized by class folders.
    *   `MyModels/`: Directory where trained `.h5` models are saved.
    *   `MyModels/graphs/`: Stores generated metric graphs (Accuracy/Loss curves).

### 2. Automated Data Splitting
A custom script automatically partitions the dataset into Train, Validation, and Test sets to ensure robust evaluation.
*   **Split Ratio**:
    *   **70% Training**: Used for model learning.
    *   **20% Validation**: Used for hyperparameter tuning during training.
    *   **10% Testing**: Reserved for final performance evaluation.
*   **Process**: The script randomly shuffles files in the source `train` folder and *moves* the respective percentages to newly created `validation` and `test` directories this ensures no data leakage between sets.

## ⚠️ IMPORTANT: Prerequisite Setup
**Before running the web application, you must train the models.**

1.  **Open the Jupyter Notebook**:
    *   Upload `Malay_Traditional_Delicacies_Recognition_System.ipynb` to **Google Colab**.
2.  **Mount Drive & Train**:
    *   Follow the instructions in the notebook to mount your Google Drive and execute the training cells.
    *   The notebook handles data splitting, training (AlexNet, ResNet50, etc.), and evaluation.
3.  **Save Trained Models**:
    *   After training, download the best-performing models (e.g., `ResNet50_FT.h5`) from your Drive.
    *   Place them in the local `MyModels/` directory of this project.
    *   *Note: The system requires these `.h5` files to perform predictions.*

## 🛠️ Technology Stack

*   **Backend**: Flask (Python)
*   **Frontend**: HTML5, TailwindCSS, DaisyUI, JavaScript (Chart.js)
*   **AI/ML Framework**: TensorFlow, Keras
*   **Data Processing**: NumPy, Pandas, Scikit-learn, OpenCV
*   **Environment**: Windows / Linux

## 🚀 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/malay-delicacies-recognition.git
    cd malay-delicacies-recognition
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application**
    ```bash
    python app.py
    ```

5.  **Access the App**
    Open your browser and navigate to `http://127.0.0.1:5000/`.

## 📂 Project Structure

```
├── .venv/                 # Virtual Environment
├── MyModels/              # Trained Model Files (.h5)
│   └── graphs/            # Training History & Confusion Matrices
├── static/                # CSS, JS, Images, Uploads
├── templates/             # HTML Templates (Jinja2)
├── app.py                 # Main Flask Application
├── routes.py              # Application Routes & Logic
├── model_utils.py         # Model Loading & Inference Logic
├── model_metrics.json     # Stored Performance Metrics
└── README.md              # Documentation
```

## 👥 Usage Guide

1.  **User Mode**:
    *   Go to **Recognize** to upload a photo of a Kuih.
    *   View results instantly with confidence scores and nutritional info.
    *   Explore the **Library** to learn about different delicacies.
2.  **Admin Mode**:
    *   Login via `/login` (default creds: `admin`/`admin`).
    *   Access `/admin/dashboard` to view system health and switch active models.
    *   Visit `/admin/evaluation` to compare detailed model performance metrics.

---
*Developed for Final Year Project (FYP)*
