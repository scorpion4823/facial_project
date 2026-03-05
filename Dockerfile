FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    python3-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel cmake

ENV MAKEFLAGS="-j1"
ENV CMAKE_BUILD_PARALLEL_LEVEL=1

# Télécharger et extraire dlib
RUN pip download dlib==19.24.2 --no-binary dlib -d /tmp/dlib_src
RUN cd /tmp/dlib_src && tar -xzf dlib-19.24.2.tar.gz

# Patcher TOUS les CMakeLists.txt
RUN find /tmp/dlib_src/dlib-19.24.2 -name "CMakeLists.txt" | \
    xargs sed -i 's/cmake_minimum_required(VERSION 2\.[0-9]*)/cmake_minimum_required(VERSION 3.5)/g'

# Ajouter le flag cmake manquant
RUN find /tmp/dlib_src/dlib-19.24.2 -name "CMakeLists.txt" | \
    xargs sed -i 's/cmake_minimum_required(VERSION 3\.[0-4])/cmake_minimum_required(VERSION 3.5)/g'

RUN cd /tmp/dlib_src/dlib-19.24.2 && \
    pip install --no-cache-dir . \
    --config-settings="cmake.args=-DCMAKE_POLICY_VERSION_MINIMUM=3.5"

RUN pip install --no-cache-dir face-recognition

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input

EXPOSE 10000

CMD ["gunicorn", "facial_project.wsgi:application", "--bind", "0.0.0.0:10000", "--timeout", "120", "--workers", "1"]