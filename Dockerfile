FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    python3-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel

# Fix CMake compatibility issue
ENV CMAKE_POLICY_VERSION_MINIMUM=3.5

RUN pip install --no-cache-dir dlib==19.24.6

RUN pip install --no-cache-dir face-recognition

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input

EXPOSE 10000

CMD ["gunicorn", "facial_project.wsgi:application", "--bind", "0.0.0.0:10000"]