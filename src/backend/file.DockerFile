FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask flask-cors pandas

EXPOSE 5000

CMD ["python", "app.py"]

