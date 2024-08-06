import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'crop_recommendation_model.pkl')

model = joblib.load(MODEL_PATH)

def predict_crop(features):
    return model.predict([features])[0]