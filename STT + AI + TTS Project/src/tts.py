import pyttsx3

def hablar(texto: str):
    motor = pyttsx3.init()

    motor.say(texto)
    motor.runAndWait()
    motor.stop()