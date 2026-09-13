FROM python:3.10-slim

# Evitar prompts de instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema para procesamiento de audio (libsndfile y ffmpeg)
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copiar requerimientos
COPY requirements.txt .

# Actualizar pip para evitar errores de compilación
RUN pip install --upgrade pip

# 1. Instalar PyTorch con soporte para CUDA 12.4+ (Compatible con Blackwell SM100 / RTX 50 series)
RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu124

# 2. Instalar el resto de dependencias (incluyendo NeMo)
RUN pip install -r requirements.txt

CMD ["bash"]
