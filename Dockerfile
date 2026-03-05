FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install --no-cache-dir \
    https://github.com/Stark-Industries0417/dlib_wheels/releases/download/v19.24.1/dlib-19.24.1-cp311-cp311-linux_x86_64.whl

RUN pip install --no-cache-dir face-recognition

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input

EXPOSE 10000

CMD ["gunicorn", "facial_project.wsgi:application", "--bind", "0.0.0.0:10000", "--timeout", "120", "--workers", "1"]