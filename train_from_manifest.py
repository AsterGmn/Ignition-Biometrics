import os
import argparse
import pandas as pd
import numpy as np
import pickle
import soundfile as sf
import librosa
import uuid
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import nemo.collections.asr as nemo_asr
import logging

logging.getLogger('nemo_logger').setLevel(logging.ERROR)

def main(csv_path, audio_folder, output_model):
    if not os.path.exists(csv_path):
        print(f"Error: No se encontró el archivo CSV {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    print("Cargando modelo TitaNet...")
    speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(model_name="titanet_large")
    speaker_model.eval()

    embeddings = []
    labels = []
    
    print(f"Procesando {len(df)} audios desde el manifiesto...")
    
    for index, row in df.iterrows():
        anon_id = row['anon_id']
        label_str = row['label']
        
        # Etiqueta: 1 para humano, 0 para sintético (IA)
        y_label = 1 if label_str.lower() == 'human' else 0
        
        # Asumimos que el archivo termina en .wav
        file_path = os.path.join(audio_folder, f"{anon_id}.wav")
        
        if not os.path.exists(file_path):
            print(f"Advertencia: Archivo no encontrado {file_path}")
            continue
            
        try:
            # Leer el audio
            y, sr = librosa.load(file_path, sr=16000, mono=False)
            
            # Extraer solo el canal 0
            if y.ndim > 1:
                y_caller = y[0, :]
            else:
                y_caller = y
            
            # OPCCIÓN 2: Simular ruido telefónico en audios demasiado limpios (Data Augmentation)
            filename = os.path.basename(file_path)
            if "laptop_human" in filename or "f5_tts" in filename or "fake_" in filename:
                noise_amp = 0.005 * np.random.uniform(0.5, 1.5)
                y_caller = y_caller + noise_amp * np.random.normal(size=y_caller.shape)
                
            # --- CHUNKING: Cortar en pedazos de 4 segundos ---
            chunk_length = 4 * 16000
            # Tomamos los primeros 5 pedazos (20 segundos totales) de cada llamada para balancear
            num_chunks = min(5, len(y_caller) // chunk_length)
            
            if num_chunks == 0:
                chunks = [y_caller] # Si el audio es muy cortito, tomamos lo que haya
            else:
                chunks = [y_caller[i*chunk_length:(i+1)*chunk_length] for i in range(num_chunks)]
                
            for chunk in chunks:
                temp_file = f"temp_{uuid.uuid4().hex}.wav"
                sf.write(temp_file, chunk, 16000)
                
                emb = speaker_model.get_embedding(temp_file)
                embeddings.append(emb.squeeze().cpu().detach().numpy())
                labels.append(y_label)
                
                os.remove(temp_file)
            
        except Exception as e:
            print(f"Error procesando {file_path}: {e}")
            
    # --- AGREGAR AUDIOS DEL LAPTOP (DATA AUGMENTATION) ---
    if os.path.exists("dataset_laptop"):
        laptop_files = [os.path.join("dataset_laptop", f) for f in os.listdir("dataset_laptop") if f.endswith('.wav')]
        if laptop_files:
            print(f"Incorporando {len(laptop_files)} audios de alta definición (Micrófono Laptop) como clase HUMANA...")
            for lf in laptop_files:
                try:
                    y, sr = librosa.load(lf, sr=16000, mono=True)
                    chunk_length = 4 * 16000
                    num_chunks = min(5, len(y) // chunk_length)
                    if num_chunks == 0: chunks = [y]
                    else: chunks = [y[i*chunk_length:(i+1)*chunk_length] for i in range(num_chunks)]
                    
                    for chunk in chunks:
                        temp_file = f"temp_{uuid.uuid4().hex}.wav"
                        sf.write(temp_file, chunk, 16000)
                        emb = speaker_model.get_embedding(temp_file)
                        embeddings.append(emb.squeeze().cpu().detach().numpy())
                        labels.append(1) # SIEMPRE ES HUMANO
                        os.remove(temp_file)
                except Exception as e:
                    print(f"Error procesando {lf}: {e}")
                    
    # --- AGREGAR AUDIOS FALSOS EXTRA (DATA AUGMENTATION IA) ---
    if os.path.exists("audios_ia_falsos"):
        fake_files = [os.path.join("audios_ia_falsos", f) for f in os.listdir("audios_ia_falsos") if f.endswith('.wav')]
        if fake_files:
            print(f"Incorporando {len(fake_files)} audios generados por IA (Extra) como clase FALSA...")
            for ff in fake_files:
                try:
                    y, sr = librosa.load(ff, sr=16000, mono=True)
                    chunk_length = 4 * 16000
                    num_chunks = min(5, len(y) // chunk_length)
                    if num_chunks == 0: chunks = [y]
                    else: chunks = [y[i*chunk_length:(i+1)*chunk_length] for i in range(num_chunks)]
                    
                    for chunk in chunks:
                        temp_file = f"temp_{uuid.uuid4().hex}.wav"
                        sf.write(temp_file, chunk, 16000)
                        emb = speaker_model.get_embedding(temp_file)
                        embeddings.append(emb.squeeze().cpu().detach().numpy())
                        labels.append(0) # SIEMPRE ES FALSO (IA)
                        os.remove(temp_file)
                except Exception as e:
                    print(f"Error procesando {ff}: {e}")
                    
    X = np.array(embeddings)
    y = np.array(labels)
    
    if len(X) == 0:
        print("Error: No se pudieron extraer características de ningún audio.")
        return
        
    print(f"\nEntrenando modelo con {len(X)} muestras...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train, y_train)
    
    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"✅ Entrenamiento completado. Precisión del modelo: {acc*100:.2f}%")
    
    with open(output_model, 'wb') as f:
        pickle.dump(clf, f)
    print(f"✅ Modelo guardado exitosamente como {output_model}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrenar leyendo desde un archivo CSV")
    parser.add_argument("--csv", required=True, help="Ruta al archivo manifest.csv")
    parser.add_argument("--folder", required=True, help="Carpeta que contiene los audios .wav")
    parser.add_argument("--output", default="anti_spoofing_model.pkl", help="Nombre del modelo final a guardar")
    args = parser.parse_args()
    
    main(args.csv, args.folder, args.output)
