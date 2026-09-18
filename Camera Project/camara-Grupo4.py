import cv2
import numpy as np

import time
from datetime import datetime
import os

testing = True
videoCaptureSource = 0 if not testing else "testVideo.mp4"

def crearDirectorios():
    carpetas = ['data/videos', 'data/fotos']

    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)


def ponerTexto(frame, texto, color):
    cv2.putText(
        frame, texto, (20, 40), 
        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 5
    )

    cv2.putText(
        frame, texto, (20, 40), 
        cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2
    )


def definirControles(frame, grabando):
    controles = [
        "q: Salir",
        "p: Tomar foto",
        "t: Tomar foto con temporizador (5 seg)",
        "r: Empezar grabacion" if not grabando else "r: Finalizar grabacion",
        "v: Empezar grabacion con temporizador (5 seg)"
    ]

    altura_extra = 180
    h, w = frame.shape[:2]

    canvas = np.zeros((h + altura_extra, w, 3), dtype=np.uint8)
    canvas[:h, :] = frame

    cv2.rectangle(canvas, (0, h), (w, h + altura_extra), (30, 30, 30), -1)

    cv2.putText(
        canvas, "CONTROLES", (20, h + 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2
    )

    y = h + 60

    for control in controles:
        cv2.putText(
            canvas, control, (20, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1
        )

        y += 25

    return canvas


def main():
    crearDirectorios()

    FPS = 20.0

    cap = cv2.VideoCapture(videoCaptureSource)

    if not cap.isOpened():
        print("ERROR: No se encontro la camara.")
        exit()

    grabando = False
    video_writer = None

    fotoTemporizador = False
    fotoTempTiempo = 0
    grabTemporizador = False
    grabTempTiempo = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            print("ERROR: Failed to read frame.")

            break

        frameActual = frame.copy()

        if fotoTemporizador:
            tiempoRestante = int(fotoTempTiempo - time.time()) + 1

            ponerTexto(frameActual, f"Foto en {tiempoRestante}", (204, 165, 75))

            if time.time() >= fotoTempTiempo:
                filename = f"data/fotos/foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)
                fotoTemporizador = False

        if grabTemporizador:
            tiempoRestante = int(grabTempTiempo - time.time()) + 1

            ponerTexto(frameActual, f"Grabacion en {tiempoRestante}", (0, 0, 255))

            if time.time() >= grabTempTiempo:
                filename = f"data/videos/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"

                fourcc = cv2.VideoWriter_fourcc(*'XVID')

                video_writer = cv2.VideoWriter(
                    filename, fourcc, FPS, (frame.shape[1], frame.shape[0])
                )

                grabando = True
                grabTemporizador = False

        if grabando:
            video_writer.write(frame)

            ponerTexto(frameActual, "o REC", (0, 0, 255))
        
        frameConControles = definirControles(frameActual, grabando)
        cv2.imshow("Camara - Grupo 4", frameConControles)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        elif key == ord('p'):
            if not fotoTemporizador:
                filename = f"data/fotos/foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

                cv2.imwrite(filename, frame)

        elif key == ord('t'):
            if not fotoTemporizador:
                fotoTemporizador = True
                fotoTempTiempo = time.time() + 5

        elif key == ord('r'):
            if not grabando and not grabTemporizador:
                filename = f"data/videos/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
                fourcc = cv2.VideoWriter_fourcc(*'XVID')

                video_writer = cv2.VideoWriter(
                    filename, fourcc, FPS, (frame.shape[1], frame.shape[0])
                )

                grabando = True
            else:
                grabando = False

                if video_writer:
                    video_writer.release()
                    video_writer = None

        elif key == ord('v'):
            if not grabando:
                grabTemporizador = True
                grabTempTiempo = time.time() + 5

    cap.release()

    if video_writer:
        video_writer.release()

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()