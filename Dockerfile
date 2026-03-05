FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel

# Installer dlib via wheel précompilé (pas de compilation)
RUN pip install --no-cache-dir \
    "dlib @ https://github.com/z-mahmud22/Dlib_Windows_Python3.x/releases/download/v19.24.2/dlib-19.24.2-cp311-cp311-linux_x86_64.whl"

RUN pip install --no-cache-dir face-recognition

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input

EXPOSE 10000

CMD ["gunicorn", "facial_project.wsgi:application", "--bind", "0.0.0.0:10000"]