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

RUN pip install --upgrade pip setuptools wheel

ENV MAKEFLAGS="-j1"
ENV CMAKE_BUILD_PARALLEL_LEVEL=1

# Patcher dlib pour corriger l'incompatibilité cmake
RUN pip install --no-cache-dir cmake
RUN pip download dlib==19.24.2 --no-binary dlib -d /tmp/dlib_src
RUN cd /tmp/dlib_src && tar -xzf dlib-19.24.2.tar.gz
RUN sed -i 's/cmake_minimum_required(VERSION 2.8.12)/cmake_minimum_required(VERSION 3.5)/g' \
    /tmp/dlib_src/dlib-19.24.2/dlib/external/pybind11/CMakeLists.txt
RUN cd /tmp/dlib_src/dlib-19.24.2 && pip install --no-cache-dir .

RUN pip install --no-cache-dir face-recognition

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input

EXPOSE 10000

CMD ["gunicorn", "facial_project.wsgi:application", "--bind", "0.0.0.0:10000", "--timeout", "120", "--workers", "1"]