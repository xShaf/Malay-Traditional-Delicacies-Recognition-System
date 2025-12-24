import os
import json
import logging
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
from models import db, User, DelicacyInfo

# --- GLOBAL VARIABLES ---
MODEL_PATHS = {
    "AlexNet (Base)": "AlexNet_v1.h5",
    "ResNet50 (Base)": "ResNet50_v1.h5",
    "MobileNetV2 (Base)": "MobileNetV2_v1.h5",
    "EfficientNetB0 (Base)": "EfficientNetB0_v1.h5",
    "ResNet50 (Fine-Tuned)": "ResNet50_v1_ft.keras",
    "MobileNetV2 (Fine-Tuned)": "MobileNetV2_v1_ft.keras",
    "EfficientNetB0 (Fine-Tuned)": "EfficientNetB0_v1_ft.keras"
}

CLASS_NAMES = sorted([
    "kuih_kaswi_pandan", "kuih_ketayap", "kuih_lapis", "kuih_seri_muka", "kuih_talam", "kuih_ubi_kayu", "onde_onde"
])

DISPLAY_NAMES = {
    "kuih_kaswi_pandan": "Kuih Kaswi Pandan",
    "kuih_ketayap": "Kuih Ketayap",
    "kuih_lapis": "Kuih Lapis",
    "kuih_seri_muka": "Kuih Seri Muka",
    "kuih_talam": "Kuih Talam",
    "kuih_ubi_kayu": "Kuih Ubi Kayu",
    "onde_onde": "Onde Onde"
}

SYSTEM_STATE = {
    "is_active": False,
    "current_model_name": "ResNet50 (Fine-Tuned)",
    "loaded_model": None
}


def prepare_image(img_path, model_name):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)

    if "AlexNet" in model_name:
        return img_array / 255.0
    elif "ResNet50" in model_name:
        return resnet_preprocess(img_array)
    elif "MobileNetV2" in model_name:
        return mobilenet_preprocess(img_array)
    elif "EfficientNetB0" in model_name:
        return efficientnet_preprocess(img_array)
    else:
        return img_array / 255.0


def load_model_metrics(app_root):
    try:
        json_path = os.path.join(app_root, 'model_metrics.json')
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)
        else:
            logging.warning("model_metrics.json not found. Using empty data.")
            return {}
    except Exception as e:
        logging.error(f"Error loading metrics: {e}")
        return {}


def init_db_data():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='adminpassword', is_admin=True)
        db.session.add(admin)
        logging.info("Created default admin account.")

    if not DelicacyInfo.query.filter_by(name="Kek Lapis Sarawak").first():
        # ... (Insert your long list of delicacies here) ...
        # For brevity, I'm including just one example, but you should copy the full list from your original file
        delicacies = [
            DelicacyInfo(
                name="Kek Lapis Sarawak",
                description="🎂 An intricate, multi-colored layer cake with geometric patterns.",
                history="A Sarawakian cultural icon evolving from the Indonesian Lapis Legit. Uniquely features vibrant colors and complex weaving patterns. It holds Geographical Indication (GI) status.",
                ingredients="450g Butter (High Quality)\n10 Eggs\nCondensed Milk & Hong Kong Flour\nHawflakes (Asam Manis)",
                recipe="1. Beat butter and sugar for 10 mins (creaming method).\n2. Bake first layer.\n3. Change oven to GRILL mode.\n4. Press, layer, and grill each subsequent layer for 5 mins."
            ),
            DelicacyInfo(
                name="Kuih Kaswi Pandan",
                description="🍮 A wobbly, dark green steamed cake coated in fresh coconut.",
                history="A 'wet kuih' known for its extreme 'gedik' (wobble). The texture relies on a balance of Tapioca flour and Alkaline water (Air Kapur).",
                ingredients="Wheat Flour & Tapioca Flour\nPandan Juice\nAlkaline Water (Crucial for bounce)\nGrated Coconut",
                recipe="1. Mix flours with alkaline water and pandan juice.\n2. Steam for 30 mins (cover lid with cloth).\n3. Cool completely for 4 hours before cutting."
            ),
            DelicacyInfo(
                name="Kuih Ketayap",
                description="🥞 Green porous crepes rolled with a sweet coconut filling.",
                history="Also known as Kuih Dadar. The skin must have 'pores' (lubang-lubang) to grip the filling, achieved by pouring batter onto a hot pan.",
                ingredients="Flour, Egg, Pandan Juice (Crepe)\nFresh Coconut, Gula Melaka (Filling)",
                recipe="1. Cook moist coconut and gula melaka filling.\n2. Pour batter on hot pan to create pores.\n3. Roll tight like a spring roll."
            ),
            DelicacyInfo(
                name="Kuih Lapis",
                description="🥢 Steamed pink and white pudding that peels apart layer by layer.",
                history="A Peranakan favorite. Usually has 9 layers symbolizing longevity. Uses a high ratio of Tapioca flour to allow layers to be peeled cleanly.",
                ingredients="Rice Flour & Tapioca Flour\nCoconut Milk\nSugar & Salt",
                recipe="1. Boil coconut milk and let cool.\n2. Steam white layer 5 mins.\n3. Steam red layer 5 mins.\n4. Repeat until finished."
            ),
            DelicacyInfo(
                name="Kuih Seri Muka",
                description="🤩 Two-layered dessert: savory sticky rice below, sweet green custard above.",
                history="Means 'Radiant Face'. The challenge is a smooth custard top. Rice must be compacted firmly to prevent the custard from seeping through.",
                ingredients="Glutinous Rice (Bottom)\nCoconut Milk, Eggs, Pandan, Cornstarch (Top)",
                recipe="1. Steam rice and COMPACT firmly into pan.\n2. Double-boil custard mixture slightly.\n3. Pour over rice and steam gently on low heat."
            ),
            DelicacyInfo(
                name="Kuih Talam Pandan",
                description="💚 A tray cake with a sweet green bottom and salty white top.",
                history="Means 'Tray Cake'. Unlike Seri Muka, both layers are smooth flour custards. The white layer uses Green Pea Flour for a silky texture.",
                ingredients="Rice/Tapioca Flour (Green)\nRice/Green Pea Flour (White)\nAlkaline Water",
                recipe="1. Steam green layer 15 mins.\n2. Scratch surface lightly (to bond).\n3. Pour white mixture and steam 20 mins."
            ),
            DelicacyInfo(
                name="Kuih Ubi Kayu",
                description="🍠 Baked Cassava cake with a dark, caramelized crust.",
                history="Also known as Bingka Ubi. A WWII survival crop turned delicacy. The dark brown 'burnt' top is prized for its caramel flavor.",
                ingredients="1kg Grated Cassava (Squeezed)\nThick Coconut Milk\nButter & Sugar",
                recipe="1. Mix squeezed cassava with ingredients.\n2. Bake at 200°C for 1 hour.\n3. Grill last 5 mins to achieve dark crust."
            ),
            DelicacyInfo(
                name="Onde Onde",
                description="💥 Green rice balls that burst with liquid palm sugar.",
                history="Also known as Buah Melaka. An 'action food' where the center must be liquid. Origins trace back to Java (Klepon).",
                ingredients="Glutinous Rice Flour\nWarm Pandan Water\nSolid Gula Melaka Cubes",
                recipe="1. Knead dough with warm water.\n2. Encase sugar cube carefully (no cracks).\n3. Boil until float + 1 minute.\n4. Roll in coconut."
            )
        ]

        for d in delicacies:
            db.session.add(d)
        logging.info("Populated database with delicacies.")

    db.session.commit()