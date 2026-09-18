import cv2
import cv2.aruco as aruco

# Generar un marcador ArUco para imprimir o mostrar en pantalla
# Usamos el diccionario 6X6_250 que tienes configurado en el script principal
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
# Generamos el ID 0
marker_img = aruco.generateImageMarker(aruco_dict, 0, 400)

# Agregamos un margen blanco para mejorar la detección en fotos impresas o capturadas con cámara.
border_size = 80
marker_with_border = cv2.copyMakeBorder(
	marker_img,
	border_size,
	border_size,
	border_size,
	border_size,
	cv2.BORDER_CONSTANT,
	value=255,
)

cv2.imwrite("marker_6x6_id0.png", marker_with_border)
print("Se ha guardado 'marker_6x6_id0.png'.")
print("IMPORTANTE: Debes usar un marcador del diccionario 6x6 para que aruco-qr.py lo detecte.")
