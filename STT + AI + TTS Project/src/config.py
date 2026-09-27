import pyaudio

# Configuracion para grabar audio

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 16kHz
CHUNK = 1024
OUTPUT_PATH = 'data/mic_audio.wav'

# Configuracion de faster_whisper (SST)
MODE = 'cuda' # Puede ser 'cpu' o 'cuda'