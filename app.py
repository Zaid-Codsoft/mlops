from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Global variables for model and preprocessors
model = None
label_encoders = {}
scaler = None

def load_model():
    """Load the trained model and preprocessors"""
    global model, label_encoders, scaler
    
    try:
        # Load the trained model
        model = joblib.load('models/churn_model.pkl')
        
        # Load label encoders
        label_encoders = joblib.load('models/label_encoders.pkl')
        
        # Load scaler
        scaler = joblib.load('models/scaler.pkl')
        
        print("Model and preprocessors loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return False

def preprocess_input(data):
    """Preprocess input data for prediction"""
    try:
        # Create DataFrame from input data
        df = pd.DataFrame([data])
        
        # Apply label encoding for categorical variables
        categorical_columns = ['gender', 'Partner', 'Dependents', 'PhoneService', 
                             'MultipleLines', 'InternetService', 'OnlineSecurity',
                             'OnlineBackup', 'DeviceProtection', 'TechSupport',
                             'StreamingTV', 'StreamingMovies', 'Contract',
                             'PaperlessBilling', 'PaymentMethod']
        
        for col in categorical_columns:
            if col in df.columns and col in label_encoders:
                df[col] = label_encoders[col].transform(df[col])
        
        # Handle missing values
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df['TotalCharges'].fillna(df['MonthlyCharges'], inplace=True)
        
        # Feature engineering (same as in training)
        df['NEW_Engaged'] = df['Contract'].apply(lambda x: 1 if x in [1, 2] else 0)  # Assuming encoded values
        df['NEW_TotalServices'] = (df[['PhoneService', 'OnlineSecurity', 'OnlineBackup',
                                      'DeviceProtection', 'TechSupport', 'StreamingTV',
                                      'StreamingMovies']] == 1).sum(axis=1)
        
        # Select features for prediction (same as training)
        feature_columns = ['SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges',
                          'gender', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
                          'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                          'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract',
                          'PaperlessBilling', 'PaymentMethod', 'NEW_Engaged', 'NEW_TotalServices']
        
        # Ensure all required columns are present
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        X = df[feature_columns]
        
        # Apply scaling
        X_scaled = scaler.transform(X)
        
        return X_scaled
        
    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        return None

@app.route('/')
def home():
    """Home page with prediction form"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for churn prediction"""
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Get input data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Preprocess input
        X = preprocess_input(data)
        
        if X is None:
            return jsonify({'error': 'Error in data preprocessing'}), 400
        
        # Make prediction
        prediction = model.predict(X)[0]
        probability = model.predict_proba(X)[0]
        
        # Return results
        result = {
            'prediction': int(prediction),
            'churn_probability': float(probability[1]),
            'no_churn_probability': float(probability[0]),
            'message': 'Customer will churn' if prediction == 1 else 'Customer will not churn'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

@app.route('/model_info')
def model_info():
    """Get model information"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({
        'model_type': type(model).__name__,
        'features': len(label_encoders) if label_encoders else 0,
        'status': 'loaded'
    })

if __name__ == '__main__':
    # Load model on startup
    if load_model():
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Failed to load model. Please check model files.")
