    FROM python:3.12.8-slim

    RUN pip install numpy pandas python-dotenv dask xgboost scikit-learn 

    WORKDIR /app

    EXPOSE 8000


    CMD ["python", "main.py"]