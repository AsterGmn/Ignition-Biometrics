import os
import glob
import torch
import librosa
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import nemo.collections.asr as nemo_asr

def load_audio(file_path, target_sr=16000):
    """Carga y resamplea el audio al formato esperado por NeMo (16kHz, mono)"""
    audio, _ = librosa.load(file_path, sr=target_sr, mono=True)
    return audio

def extract_embeddings(model, data_dir):
    """Extrae embeddings de audios reales y generados (fakes)."""
    embeddings = []
    labels = []
    
    # Clases: 1 = Real, 0 = Fake (IA)
    classes = {'real': 1, 'fake': 0}
    
    for class_name, label in classes.items():
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.exists(class_dir):
            print(f"Advertencia: No se encontró el directorio {class_dir}")
            continue
            
        audio_files = glob.glob(os.path.join(class_dir, "*.wav"))
        print(f"Procesando {len(audio_files)} archivos de la clase '{class_name}'...")
        
        for file_path in audio_files:
            try:
                # Extraemos el embedding directamente del archivo usando TitaNet
                # TitaNet extrae un vector de características robustas de la voz del hablante.
                # Nota: NeMo espera listas de rutas de audio para inferencia en batch, 
                # pero get_embedding acepta un archivo simple si ajustamos el uso.
                # get_embedding devuelve un tensor de PyTorch.
                embedding = model.get_embedding(file_path)
                
                # Convertimos el tensor a un array de NumPy (1D)
                emb_np = embedding.squeeze().cpu().detach().numpy()
                embeddings.append(emb_np)
                labels.append(label)
            except Exception as e:
                print(f"Error procesando {file_path}: {e}")
                
    return np.array(embeddings), np.array(labels)

def main():
    print("Cargando modelo TitaNet para extracción de características...")
    # TitaNet-Large genera embeddings de tamaño 192.
    speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(model_name="titanet_large")
    speaker_model.eval()
    
    # Asumimos que los audios están en ./dataset/real/ y ./dataset/fake/
    dataset_dir = "./dataset"
    print(f"Extrayendo características de audios en {dataset_dir}...")
    X, y = extract_embeddings(speaker_model, dataset_dir)
    
    if len(X) == 0:
        print("No se encontraron audios válidos. Asegúrate de tener archivos .wav en dataset/real/ y dataset/fake/.")
        return
        
    print(f"Extraídos {len(X)} audios en total. Entrenando clasificador...")
    
    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Usar Regresión Logística (o SVM)
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train, y_train)
    
    # Evaluar
    y_pred = clf.predict(X_test)
    print("\nReporte de Clasificación:")
    print(classification_report(y_test, y_pred, target_names=['Fake (IA)', 'Real']))
    print(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
    
    # Guardar el modelo
    model_path = "anti_spoofing_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(clf, f)
    print(f"Modelo clasificador guardado en {model_path}")

if __name__ == "__main__":
    main()
