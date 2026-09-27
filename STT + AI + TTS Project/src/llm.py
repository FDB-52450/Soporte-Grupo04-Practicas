import json

from ollama import chat
from src.models import DatosEntrevista

MODEL = "gemma3:12b-it-qat"

def system_prompt(configuracion: DatosEntrevista) -> str:
    tema = configuracion.temas[configuracion.pregunta_actual - 1]

    return f"""
        Eres un reclutador experto de la empresa {configuracion.nombre_empresa}, estas entrevistando a {configuracion.nombre_entrevistado} 
        ({configuracion.edad_entrevistado} años) para el puesto de {configuracion.puesto} ({configuracion.nivel}).
        La entrevista tiene {configuracion.total_preguntas} preguntas. Esta es la pregunta {configuracion.pregunta_actual}.
        El tema de esta pregunta es: {tema}.

        Devuelve una respuesta breve y hablada en español. Evalúa la respuesta anterior con la
        transcripción y métricas de audio recibidas. Después, formula exactamente una pregunta
        para el tema actual. No inventes información sobre el candidato.

        La respuesta devuelta no debe contener ningun simbolo especial, ya sea astericos, signos de exclamacion, o cualquier otro.
        No dejar placeholders para el nombre del entrevistador, generar un nombre generico de un ciudadano argentino (masculino o femenino)
    """.strip()


def ask_llm(configuracion: DatosEntrevista, prompt: str) -> str:
    messages = [{"role": "system", "content": system_prompt(configuracion)}]
    messages.extend(configuracion.historial)
    messages.append({"role": "user", "content": prompt})

    response = chat(
        model=MODEL,
        messages=messages,
        options={"temperature": 0},
    )

    answer = response.message.content.strip()

    configuracion.historial.extend([
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": answer},
    ])

    return answer


def iniciar_entrevista(configuracion: DatosEntrevista) -> str:
    return ask_llm(configuracion, "Da una introducción breve de la entrevista y formula la primera pregunta.")


def formular_siguiente_pregunta(configuracion: DatosEntrevista, respuesta: dict) -> str:
    prompt = (
        "Esta es la respuesta del candidato a la pregunta anterior. "
        "Evalúala y formula la siguiente pregunta del plan. Datos:\n"

        f"{json.dumps(respuesta, ensure_ascii=False)}"
    )

    pregunta = ask_llm(configuracion, prompt)
    configuracion.ultima_pregunta = pregunta

    return pregunta


def cerrar_entrevista(configuracion: DatosEntrevista, respuesta_final: dict) -> str:
    prompt = (
        "La entrevista ha terminado. Evalúa la respuesta final y ofrece un resumen "
        "breve del desempeño, con fortalezas y un área de mejora. Datos:\n"

        f"{json.dumps(respuesta_final, ensure_ascii=False)}"
    )

    return ask_llm(configuracion, prompt)

