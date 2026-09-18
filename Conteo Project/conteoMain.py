import cv2
import numpy as np

from ultralytics import YOLO

# Cargar modelo YOLOv8n
model = YOLO("yolov8n.pt")

# Abrir video de prueba
cap = cv2.VideoCapture("conteoVideo.mp4")

# Definir área ignorada (polígono) - ajusta los puntos según tu video
mask_polygon = np.array([
    [640, 0],
    [640, 275],
    [425, 150],
    [225, 150],
    [0, 250],
    [0, 0]
], dtype=np.int32)

# Diccionario para mapear IDs de seguimiento a tus propios IDs
id_map = {}
next_id = 1

# Función de callback para obtener coordenadas del mouse
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"[{x}, {y}],")

while True:
    ret, frame = cap.read()

    if not ret:
        break

    masked_frame = frame.copy()

    # Fill polygon with black
    cv2.fillPoly(masked_frame, [mask_polygon], (0, 0, 0))

    #cv2.polylines(frame, [mask_polygon], isClosed = True, color = (0, 0, 255), thickness = 2)

    # Tracking para contar vehiculos
    results = model.track(masked_frame, persist = True, verbose = False)

    # Mostrar resultados
    display_frame = frame.copy()
    result = results[0]

    if result.boxes.id is not None:
        boxes = result.boxes.xyxy.cpu().numpy()
        track_ids = result.boxes.id.cpu().numpy().astype(int)

        for box, tid in zip(boxes, track_ids):
            x1, y1, x2, y2 = map(int, box)

            centroX = (x1 + x2) // 2
            centroY = (y1 + y2) // 2

            # assign your own ID
            if tid not in id_map:
                id_map[tid] = next_id
                next_id += 1

            my_id = id_map[tid]

            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (255, 173, 0), 2)

            cv2.putText(
                display_frame, f"ID: [{my_id}]", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 173, 0), 2
            )

            cv2.putText(
                display_frame, f"[{centroX}, {centroY}]", (x1, y2 + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 173, 0), 1
            )

    cv2.imshow("Conteo", display_frame)
    cv2.setMouseCallback("Conteo", mouse_callback) # Descomenta esta línea para habilitar la función de callback del mouse

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()