FROM apache/airflow:2.5.2-python3.8

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
