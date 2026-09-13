
import os
import argparse
import torch
import torchaudio
from f5_tts.api import F5TTS

def clone_voice(ref_audio: str, ref_text: str, target_text: str, output_path: str = "output.wav"):
    if not os.path.exists(ref_audio):
        raise FileNotFoundError(f"Reference audio not found at: {ref_audio}")

    print("Loading F5-TTS model...")
    tts_engine = F5TTS()

    print(f"Synthesizing text: '{target_text}'")
    wav_np, sample_rate, _ = tts_engine.infer(
        ref_file=ref_audio,
        ref_text=ref_text,
        gen_text=target_text
    )

    # Convert NumPy array to PyTorch Tensor [channels, samples]
    wav_tensor = torch.from_numpy(wav_np).unsqueeze(0)

    # Save generated audio
    torchaudio.save(output_path, wav_tensor, sample_rate)
    print(f"Audio generated successfully: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zero-shot Voice Cloning with F5-TTS")
    parser.add_argument("--ref_audio", type=str, required=True, help="Path to reference audio sample (.wav)")
    parser.add_argument("--ref_text", type=str, default="", help="Transcript of reference audio")
    parser.add_argument("--text", type=str, required=True, help="Target text to synthesize")
    parser.add_argument("--output", type=str, default="output.wav", help="Output file path")

    args = parser.parse_args()
    clone_voice(args.ref_audio, args.ref_text, args.text, args.output)
