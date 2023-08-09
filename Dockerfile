FROM apache/airflow:latest-python3.8

COPY UTX_Reports/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
