from pathlib import Path
import os

from pydub import AudioSegment
import librosa

import pyaudio
import wave

from faster_whisper import WhisperModel

from src.config import FORMAT, CHANNELS, CHUNK, RATE, OUTPUT_PATH, MODE

# Codigo de Copilot par arreglar problemas con librerias de NVIDIA (cublas)
if os.name == "nt" and MODE == 'cuda':
    import nvidia
    import nvidia.cublas
    import nvidia.cudnn

    cuda_dll_directories = [
        Path(nvidia.cublas.__path__[0]) / "bin",
        Path(nvidia.cudnn.__path__[0]) / "bin",
        Path(nvidia.__path__[0]) / "cuda_runtime" / "bin",
        Path(nvidia.__path__[0]) / "cuda_nvrtc" / "bin",
    ]
    
    for directory in cuda_dll_directories:
        if directory.exists():
            os.add_dll_directory(str(directory))
            os.environ["PATH"] = str(directory) + os.pathsep + os.environ["PATH"]


def grabar_audio_microfono():
    audio = pyaudio.PyAudio()

    stream = audio.open(format = FORMAT, channels = CHANNELS, rate = RATE, input = True, frames_per_buffer = CHUNK)
    frames = []

    try:
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
    except KeyboardInterrupt:
        pass
        
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Crea carpeta /data si no existe
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Guardar en archivo .wav
    wf = wave.open(OUTPUT_PATH, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return OUTPUT_PATH



def transcribir_con_tiempos(ruta_audio):
    model = WhisperModel("base", device = MODE, device_index = 0, compute_type = "float16")

    segments, info = model.transcribe(ruta_audio, language = "es", word_timestamps = True)

    texto_completo = ""
    palabras_detalladas = []

    for segment in segments:
        texto_completo += segment.text + " "

        for word in segment.words:
            palabras_detalladas.append({
                "palabra": word.word,
                "inicio": round(word.start, 2),
                "fin": round(word.end, 2),
                "probabilidad": round(word.probability, 2)
            })

    return texto_completo.strip(), palabras_detalladas, info.duration


def extraer_metricas_completas(ruta_audio, texto, palabras, duracion_total):
    audio = AudioSegment.from_file(ruta_audio)
    
    # 1. Ritmo de Habla (PPM)
    total_palabras = len(palabras)
    ppm = (total_palabras / duracion_total) * 60 if duracion_total > 0 else 0

    # 2. Análisis de Pausas entre palabras (>1.0 segundo)
    pausas_detectadas = []
    
    for i in range(len(palabras) - 1):
        fin_actual = palabras[i]["fin"]
        inicio_siguiente = palabras[i+1]["inicio"]
        duracion_pausa = inicio_siguiente - fin_actual
        
        if duracion_pausa >= 1.0:
            pausas_detectadas.append({
                "despues_de": palabras[i]["palabra"],
                "antes_de": palabras[i+1]["palabra"],
                "duracion_seg": round(duracion_pausa, 2)
            })

    # 3. Nivel de Volumen Promedio (RMS a dB)
    volumen_db = audio.dBFS

    return {
        "duracion_total": round(duracion_total, 2),
        "ppm": round(ppm, 1),
        "volumen_db": round(volumen_db, 1),
        "pausas": pausas_detectadas
    }


def borrar_archivo(ruta_archivo):
    if os.path.exists(ruta_archivo):
        os.remove(ruta_archivo)
    else:
        print("The file does not exist")


def detection_pipeline(ruta_archivo_wav: str = None):
    # Permite usar archivos grabados previamente
    testing = True

    if ruta_archivo_wav is None:
        ruta_archivo_wav = grabar_audio_microfono()
        testing = False

    texto, palabras, duracion = transcribir_con_tiempos(ruta_archivo_wav)
    metricas = extraer_metricas_completas(ruta_archivo_wav, texto, palabras, duracion)

    payload_para_llm = {
        "transcripcion": texto,
        "metricas": metricas
    }

    if testing:
        borrar_archivo(ruta_archivo_wav)

    return payload_para_llm


if __name__ == "__main__":
    data = detection_pipeline('data/test-audio-input-long.wav')

    print(data)
