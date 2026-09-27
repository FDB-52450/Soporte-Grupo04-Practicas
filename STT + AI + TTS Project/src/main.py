from src.text_detection import detection_pipeline
from src.llm import cerrar_entrevista, formular_siguiente_pregunta, iniciar_entrevista
from src.models import DatosEntrevista
from src.tts import hablar


def main_loop(configuracion: DatosEntrevista):
    hablar(iniciar_entrevista(configuracion))

    for pregunta in range(configuracion.total_preguntas):
        respuesta = detection_pipeline()

        if pregunta == configuracion.total_preguntas - 1:
            hablar(cerrar_entrevista(configuracion, respuesta))
            break

        configuracion.pregunta_actual += 1
        hablar(formular_siguiente_pregunta(configuracion, respuesta))


if __name__ == '__main__':
    configuracion = DatosEntrevista(
        nombre_entrevistado = 'Julian Alvarez',
        edad_entrevistado = 26,
        nombre_empresa = 'MercadoLibre',
        puesto = "Desarrollador Python",
        nivel = "junior",
        total_preguntas = 3,
        temas = ["Experiencia", "Resolución de problemas", "Trabajo en equipo"],
    )

    main_loop(configuracion)