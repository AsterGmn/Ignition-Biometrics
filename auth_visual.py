import os
import argparse
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import pickle
import torch
from sklearn.metrics.pairwise import cosine_similarity
import nemo.collections.asr as nemo_asr

def plot_spectrograms(audio_path_1, audio_path_2, title1="Voz Entrante", title2="Voz en Base de Datos", output_path="analisis_espectro.png"):
    print("Generando análisis visual de espectrogramas...")
    # Cargar audios
    y1, sr1 = librosa.load(audio_path_1, sr=16000)
    y2, sr2 = librosa.load(audio_path_2, sr=16000)
    
    # Calcular Espectrogramas de Mel
    S1 = librosa.feature.melspectrogram(y=y1, sr=sr1, n_mels=128)
    S2 = librosa.feature.melspectrogram(y=y2, sr=sr2, n_mels=128)
    
    # Convertir a decibeles
    S1_db = librosa.power_to_db(S1, ref=np.max)
    S2_db = librosa.power_to_db(S2, ref=np.max)
    
    # Graficar
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    
    img1 = librosa.display.specshow(S1_db, x_axis='time', y_axis='mel', sr=sr1, ax=ax[0], cmap='magma')
    ax[0].set(title=title1)
    
    img2 = librosa.display.specshow(S2_db, x_axis='time', y_axis='mel', sr=sr2, ax=ax[1], cmap='magma')
    ax[1].set(title=title2)
    
    fig.colorbar(img1, ax=ax, format="%+2.f dB")
    plt.savefig(output_path)
    print(f"--> ¡Gráfico de comparación guardado como '{output_path}'!")
    plt.close()

def load_anti_spoofing_model(model_path="anti_spoofing_model.pkl"):
    with open(model_path, 'rb') as f:
        clf = pickle.load(f)
    return clf

def main(incoming_audio, reference_audio, threshold=0.75):
    # 1. Visualización
    plot_spectrograms(incoming_audio, reference_audio)
    
    print("\n--- FASE 1: Detección Anti-Spoofing (Deepfake) ---")
    speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(model_name="titanet_large")
    speaker_model.eval()

    # Extraer características
    embedding_in = speaker_model.get_embedding(incoming_audio).squeeze().cpu().detach().numpy()
    embedding_ref = speaker_model.get_embedding(reference_audio).squeeze().cpu().detach().numpy()
    
    try:
        clf = load_anti_spoofing_model()
        prediction = clf.predict(embedding_in.reshape(1, -1))[0]
        if prediction == 0:
            print("[ALERTA]: El audio entrante fue GENERADO POR IA.")
            print("Acceso DENEGADO.")
            return
        else:
            print("[OK] Audio genuino humano detectado.")
    except FileNotFoundError:
        print("Advertencia: No se encontró anti_spoofing_model.pkl.")

    print("\n--- FASE 2: Autenticación Biométrica ---")
    sim = cosine_similarity(embedding_in.reshape(1, -1), embedding_ref.reshape(1, -1))[0][0]
            
    if sim >= threshold:
        print(f"[ACCESO CONCEDIDO] Las huellas vocales coinciden. (Similitud: {sim*100:.2f}%)")
    else:
        print(f"[ACCESO DENEGADO] Las voces no coinciden. (Similitud: {sim*100:.2f}%)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autenticación Visual Biométrica")
    parser.add_argument("--incoming", required=True, help="Ruta al audio que intenta ingresar")
    parser.add_argument("--reference", required=True, help="Ruta al audio original del usuario registrado")
    args = parser.parse_args()
    
    main(args.incoming, args.reference)
