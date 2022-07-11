FROM arm32v7/python:3.9.13-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ble2mqtt.py .

ENTRYPOINT ["python", "./ble2mqtt.py"]