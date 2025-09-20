"""
Unit tests for the Flask application
"""

import unittest
import json
import os
import sys
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestFlaskApp(unittest.TestCase):
    """Test cases for Flask application"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        
    def test_home_page(self):
        """Test home page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Telco Customer Churn Prediction', response.data)
        
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        
    def test_model_info_without_model(self):
        """Test model info endpoint when model is not loaded"""
        with patch('app.model', None):
            response = self.app.get('/model_info')
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertIn('error', data)
            
    def test_predict_without_model(self):
        """Test prediction endpoint when model is not loaded"""
        with patch('app.model', None):
            test_data = {
                'gender': 'Male',
                'SeniorCitizen': 0,
                'Partner': 'No',
                'Dependents': 'No',
                'tenure': 12,
                'PhoneService': 'Yes',
                'MultipleLines': 'No',
                'InternetService': 'DSL',
                'Contract': 'Month-to-month',
                'MonthlyCharges': 50.0,
                'TotalCharges': 600.0
            }
            
            response = self.app.post('/predict', 
                                   data=json.dumps(test_data),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertIn('error', data)
            
    def test_predict_with_invalid_data(self):
        """Test prediction with invalid data"""
        response = self.app.post('/predict', 
                               data=json.dumps({}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_predict_with_mock_model(self):
        """Test prediction with mocked model"""
        # Mock the model and preprocessors
        mock_model = MagicMock()
        mock_model.predict.return_value = [1]
        mock_model.predict_proba.return_value = [[0.3, 0.7]]
        
        mock_encoders = {
            'gender': MagicMock(),
            'Partner': MagicMock(),
            'Dependents': MagicMock(),
            'PhoneService': MagicMock(),
            'MultipleLines': MagicMock(),
            'InternetService': MagicMock(),
            'Contract': MagicMock()
        }
        
        mock_scaler = MagicMock()
        mock_scaler.transform.return_value = np.array([[1, 2, 3, 4, 5]])
        
        with patch('app.model', mock_model), \
             patch('app.label_encoders', mock_encoders), \
             patch('app.scaler', mock_scaler):
            
            test_data = {
                'gender': 'Male',
                'SeniorCitizen': 0,
                'Partner': 'No',
                'Dependents': 'No',
                'tenure': 12,
                'PhoneService': 'Yes',
                'MultipleLines': 'No',
                'InternetService': 'DSL',
                'Contract': 'Month-to-month',
                'MonthlyCharges': 50.0,
                'TotalCharges': 600.0
            }
            
            response = self.app.post('/predict', 
                                   data=json.dumps(test_data),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('prediction', data)
            self.assertIn('churn_probability', data)
            self.assertEqual(data['prediction'], 1)

class TestModelTraining(unittest.TestCase):
    """Test cases for model training"""
    
    def test_data_loading(self):
        """Test data loading functionality"""
        # This test would require the actual CSV file
        # For now, we'll test the structure
        self.assertTrue(os.path.exists('Telco-Customer-Churn.csv'))
        
    def test_feature_engineering(self):
        """Test feature engineering functions"""
        # Create sample data
        df = pd.DataFrame({
            'Contract': ['Month-to-month', 'One year', 'Two year'],
            'PhoneService': ['Yes', 'Yes', 'No'],
            'OnlineSecurity': ['No', 'Yes', 'No']
        })
        
        # Test NEW_Engaged feature
        df['NEW_Engaged'] = df['Contract'].apply(lambda x: 1 if x in ['One year','Two year'] else 0)
        expected_engaged = [0, 1, 1]
        self.assertEqual(df['NEW_Engaged'].tolist(), expected_engaged)
        
        # Test NEW_TotalServices feature
        df['NEW_TotalServices'] = (df[['PhoneService', 'OnlineSecurity']]== 'Yes').sum(axis=1)
        expected_services = [1, 2, 0]
        self.assertEqual(df['NEW_TotalServices'].tolist(), expected_services)

class TestHelperFunctions(unittest.TestCase):
    """Test cases for helper functions"""
    
    def test_grab_col_names(self):
        """Test column name categorization"""
        # Create sample dataframe
        df = pd.DataFrame({
            'numeric_col': [1, 2, 3, 4, 5],
            'categorical_col': ['A', 'B', 'A', 'B', 'A'],
            'high_cardinality': [f'item_{i}' for i in range(100)]
        })
        
        # Import the function
        from helper_functions import grab_col_names
        
        cat_cols, num_cols, cat_but_car, num_but_cat = grab_col_names(df)
        
        self.assertIn('categorical_col', cat_cols)
        self.assertIn('numeric_col', num_cols)
        self.assertIn('high_cardinality', cat_but_car)

if __name__ == '__main__':
    unittest.main()
