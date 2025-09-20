"""
Model training script for Telco Churn Prediction
This script trains the model and saves it for the Flask application
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

def load_and_preprocess_data():
    """Load and preprocess the telco churn dataset"""
    print("Loading data...")
    df = pd.read_csv('Telco-Customer-Churn.csv')
    
    # Basic preprocessing
    df['Churn'] = df['Churn'].apply(lambda x: 1 if x == 'Yes' else 0)
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df['TotalCharges'].fillna(df['MonthlyCharges'], inplace=True)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Churn rate: {df['Churn'].mean():.2%}")
    
    return df

def feature_engineering(df):
    """Apply feature engineering"""
    print("Applying feature engineering...")
    
    # Create new features
    df['NEW_Engaged'] = df['Contract'].apply(lambda x: 1 if x in ['One year','Two year'] else 0)
    df['NEW_TotalServices'] = (df[['PhoneService', 'OnlineSecurity', 'OnlineBackup',
                                  'DeviceProtection', 'TechSupport', 'StreamingTV',
                                  'StreamingMovies']]== 'Yes').sum(axis=1)
    
    return df

def encode_categorical_features(df):
    """Encode categorical features"""
    print("Encoding categorical features...")
    
    categorical_columns = ['gender', 'Partner', 'Dependents', 'PhoneService', 
                          'MultipleLines', 'InternetService', 'OnlineSecurity',
                          'OnlineBackup', 'DeviceProtection', 'TechSupport',
                          'StreamingTV', 'StreamingMovies', 'Contract',
                          'PaperlessBilling', 'PaymentMethod']
    
    label_encoders = {}
    
    for col in categorical_columns:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            label_encoders[col] = le
    
    return df, label_encoders

def train_model(X, y):
    """Train the Random Forest model"""
    print("Training Random Forest model...")
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train the model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    
    print("\nModel Performance:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    return model, scaler, X_test_scaled, y_test

def save_model_and_preprocessors(model, label_encoders, scaler):
    """Save the trained model and preprocessors"""
    print("Saving model and preprocessors...")
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Save the model
    joblib.dump(model, 'models/churn_model.pkl')
    
    # Save label encoders
    joblib.dump(label_encoders, 'models/label_encoders.pkl')
    
    # Save scaler
    joblib.dump(scaler, 'models/scaler.pkl')
    
    print("Model and preprocessors saved successfully!")

def main():
    """Main training pipeline"""
    print("Starting Telco Churn Prediction Model Training...")
    
    # Load and preprocess data
    df = load_and_preprocess_data()
    
    # Feature engineering
    df = feature_engineering(df)
    
    # Encode categorical features
    df, label_encoders = encode_categorical_features(df)
    
    # Prepare features and target
    feature_columns = ['SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges',
                      'gender', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
                      'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                      'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract',
                      'PaperlessBilling', 'PaymentMethod', 'NEW_Engaged', 'NEW_TotalServices']
    
    X = df[feature_columns]
    y = df['Churn']
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    # Train the model
    model, scaler, X_test, y_test = train_model(X, y)
    
    # Save model and preprocessors
    save_model_and_preprocessors(model, label_encoders, scaler)
    
    print("\nTraining completed successfully!")
    print("Model is ready for deployment!")

if __name__ == "__main__":
    main()
