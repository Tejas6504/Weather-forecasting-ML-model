FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py model.py model.joblib elnino.csv .

CMD ["ddtrace-run", "python", "app.py"]

