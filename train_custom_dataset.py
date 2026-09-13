import os
import argparse
import glob
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import nemo.collections.asr as nemo_asr

def extract_embeddings(model, real_dir, fake_dir):
    import soundfile as sf
    import librosa
    import uuid
    embeddings, labels = [], []
    for directory, label in [(real_dir, 1), (fake_dir, 0)]:
        files = glob.glob(os.path.join(directory, "*.wav"))
        print(f"Extrayendo de {directory}: {len(files)} archivos...")
        for f in files:
            try:
                # Leer el audio (librosa lo lee como estéreo si es estéreo)
                y, sr = librosa.load(f, sr=16000, mono=False)
                # Extraer solo el canal 0 (atacante) si tiene más de 1 canal
                if y.ndim > 1:
                    y_caller = y[0, :]
                else:
                    y_caller = y
                
                # Guardar temporalmente como mono para TitaNet
                temp_file = f"temp_{uuid.uuid4().hex}.wav"
                sf.write(temp_file, y_caller, 16000)
                
                emb = model.get_embedding(temp_file)
                embeddings.append(emb.squeeze().cpu().detach().numpy())
                labels.append(label)
                
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Error procesando {f}: {e}")
    return np.array(embeddings), np.array(labels)

def main(real_dir, fake_dir, output_model):
    print("Cargando modelo TitaNet...")
    speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(model_name="titanet_large")
    speaker_model.eval()

    X, y = extract_embeddings(speaker_model, real_dir, fake_dir)
    
    if len(X) == 0:
        print("Error: No se encontraron audios.")
        return
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train, y_train)
    
    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"Modelo entrenado con Dataset Personalizado. Precisión: {acc*100:.2f}%")
    
    with open(output_model, 'wb') as f:
        pickle.dump(clf, f)
    print(f"Modelo guardado como {output_model}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrenar modelo Anti-Spoofing con dataset personalizado")
    parser.add_argument("--real", required=True, help="Carpeta con audios humanos genuinos")
    parser.add_argument("--fake", required=True, help="Carpeta con audios IA/Deepfakes")
    parser.add_argument("--output", default="anti_spoofing_model.pkl", help="Nombre del modelo final a guardar")
    args = parser.parse_args()
    
    main(args.real, args.fake, args.output)
