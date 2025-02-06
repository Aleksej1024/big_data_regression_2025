from flask import Flask, request, jsonify
import pandas as pd
import pickle
import os
import sys
from io import StringIO
from datetime import datetime


app = Flask(__name__)

# Папка с моделями
MODEL_DIR = 'models'
# Папка с данными 
DATA_DIR = 'data'

# Хранение загруженных данных
data = None
selected_model = None

@app.route('/upload', methods=['POST'])
def upload_data():
    
    global data
    file = request.files['file']
   
    try:
        # Чтение CSV из файлового объекта
        data = pd.read_csv(file.stream)  # Используем file.stream
        
        data.to_csv(f"./{DATA_DIR}/not_process_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.csv")
        return jsonify({
            "message": "Файл успешно загружен",
      
        }), 200
        
    except pd.errors.ParserError:
        return jsonify({"error": "Ошибка парсинга CSV"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/preprocess', methods=['POST'])
def preprocess_data():
    global data
    if data is not None:
        data=data.drop([ '6', '12', '13', '14', '24', '28'],axis=1)
        data=data.iloc[: , 1:]
        data=data.astype('int32')
        data.to_csv(f"./{DATA_DIR}/pre_process_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.csv")
        return jsonify({"message": "Данные успешно предобработаны"}), 200
    return jsonify({"error": "Данные не предобработаны"}), 400

@app.route('/models', methods=['GET'])
def list_models():
    models = [f for f in os.listdir(MODEL_DIR) if f.endswith('.pkl')]
    return jsonify(models), 200

@app.route('/select_model', methods=['POST'])
def select_model():
    global selected_model
    model_name = request.json.get('model_name')
    if model_name in os.listdir(MODEL_DIR):
        selected_model = model_name
        return jsonify({"message": f"Выбрана модель {model_name}"}), 200
    return jsonify({"error": "Модель не найдена"}), 404

@app.route('/predict', methods=['POST'])
def predict():
    global data, selected_model
    if data is not None and selected_model is not None:
        model_path = os.path.join(MODEL_DIR, selected_model)
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        predictions = model.predict(data)
        return jsonify(predictions.tolist()), 200
    return jsonify({"error": "Данные не загружены или модель не выбрана, попробуйте ещё"}), 400

if __name__ == '__main__':
    app.run(debug=True)
