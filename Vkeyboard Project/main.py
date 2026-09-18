import random
import string

from kivy.app import App
from kivy.properties import StringProperty, NumericProperty

from kivy.uix.popup import Popup
from kivy.uix.label import Label

class VkeyboardGameApp(App):
    # Propiedades del juego: puntaje, letra actual y estado de deshabilitado
    score = NumericProperty(0)
    currentLetter = StringProperty("")
    disabled = False

    # Inicializa el programa, asignando una letra aleatoria
    def build(self):
        self.new_letter()

    # Genera una nueva letra aleatoria para el juego
    def new_letter(self):
        self.currentLetter = random.choice(string.ascii_lowercase)

    # Maneja la entrada de texto del usuario, actualizando el puntaje y la letra actual
    def on_text_input(self, instance, text):
        # Si no es texto, volver   
        if not text:
            return

        pressed = text.lower()

        # Si el juego está deshabilitado (el jugador perdio), solo se puede reiniciar presionando "r"
        if self.disabled:
            if pressed == "r":
                self.disabled = False
                self.score = 0
                self.new_letter()
            return
        
        # Si la letra presionada es correcta, aumenta el puntaje y genera una nueva letra
        if pressed == self.currentLetter:
            self.score += 1
            self.new_letter()
        else:
            # De lo contrario, disminuye el puntaje. Si el puntaje llega a 0, deshabilita el juego y muestra un mensaje de derrota
            if self.score <= 0:
                self.disabled = True
                self.currentLetter = "-"

                self.show_game_over()
            else:
                self.score -= 1
                self.new_letter()
    
    def show_game_over(self):
        Popup(
            title="Game Over",
            content=Label(text="YOU LOST! \n [Press R to restart]", font_size=20, halign="center", valign="middle", bold=True),
            size_hint=(0.3, 0.225)
        ).open()


if __name__ == "__main__":
    VkeyboardGameApp().run()