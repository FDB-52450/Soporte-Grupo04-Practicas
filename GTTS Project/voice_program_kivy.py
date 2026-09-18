import base64
import json
import os
import random
import requests
from gtts import gTTS

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

Builder.load_file(os.path.join(os.path.dirname(__file__), "voice_program_kivy.kv"))


def ensure_cache_dir():
    os.makedirs("data/cache", exist_ok=True)


def has_internet(timeout=3):
    try:
        requests.get("https://www.google.com", timeout=timeout)
        return True
    except requests.RequestException:
        return False


def select_sentence():
    with open("data/sentences.json", "r", encoding="utf-8") as file:
        sentences = json.load(file)

    selection = random.choice(sentences)
    language, sentence = random.choice(list(selection["translations"].items()))
    return sentence, language


def select_sentence_from_cache():
    files = os.listdir("data/cache")

    if not files:
        raise FileNotFoundError(
            "No cached audio files found. Please run the program with an internet connection first."
        )

    filename = random.choice(files)
    decoded_filename = base64.urlsafe_b64decode(
        filename.replace('.mp3', '').encode("utf-8")
    ).decode("utf-8")

    sentence, language = decoded_filename.split(":", 1)

    return sentence, language, filename


def select_data():
    ensure_cache_dir()

    if has_internet():
        text, lang = select_sentence()
        tts = gTTS(text=text, lang=lang, slow=False)
        filename = (
            base64.urlsafe_b64encode(f"{text}:{lang}".encode("utf-8"))
            .decode("utf-8")
            + ".mp3"
        )
        filepath = os.path.join("data", "cache", filename)
        tts.save(filepath)
        return text, lang, filepath

    text, lang, filename = select_sentence_from_cache()
    filepath = os.path.join("data", "cache", filename)

    return text, lang, filepath


'''def playback(filepath):
    sound = SoundLoader.load(filepath)

    if sound is None:
        return False
    
    sound.play()

    return True'''


class GTTSGame(BoxLayout):
    sentence_text = StringProperty("Press START to load a sentence.")
    language_code = StringProperty("")
    feedback_text = StringProperty("Choose the language after listening.")
    status_text = StringProperty("Ready")
    timer_text = StringProperty("")
    score = NumericProperty(0)
    loops = NumericProperty(0)

    def __init__(self, **kwargs):
        self.current_sentence = ""
        self.current_language = ""
        self.current_filepath = ""
        self.timer_event = None
        self.time_left = 0

        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        self.reset_game()

    def _update_ui(self, enabled, can_retry=False, can_start=False):
        self.ids.play_button.disabled = not enabled
        self.ids.retry_button.disabled = not can_retry
        self.ids.start_button.disabled = not can_start

        for child in self.ids.language_buttons.children:
            child.disabled = not enabled

    def _start_timer(self):
        self._stop_timer()

        self.time_left = 15
        self.timer_text = f"Time left: {self.time_left}s"
        self.timer_event = Clock.schedule_interval(self._on_timer_tick, 1)

    def _stop_timer(self):
        if self.timer_event is not None:
            self.timer_event.cancel()
            self.timer_event = None

        self.timer_text = ""

    def _on_timer_tick(self, dt):
        self.time_left -= 1

        if self.time_left <= 0:
            self._stop_timer()
            self._handle_timeout()
            return False

        self.timer_text = f"Time left: {self.time_left}s"
        return True

    def _handle_timeout(self):
        if not self.current_language:
            return

        lang_types = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
        }

        full_lang_text = lang_types.get(self.current_language, self.current_language)
        self.feedback_text = f"Time's up! The correct language was {full_lang_text}."
        self.status_text = "Time expired. Press Retry."

        self._update_ui(False, can_retry=True, can_start=False)

    def on_start(self):
        self.status_text = "Loading sentence..."
        Clock.schedule_once(self.load_sentence, 0.1)

    def load_sentence(self, dt):
        try:
            text, lang, filepath = select_data()
        except Exception as exc:
            self.status_text = f"Error: {exc}"
            self._update_ui(False, can_retry=True, can_start=False)

            return

        self.current_sentence = text
        self.current_language = lang
        self.current_filepath = filepath
        self.sentence_text = self.current_sentence
        self.language_code = lang
        self.feedback_text = "Press Play Audio, then guess the language."
        self.status_text = "Sentence loaded."

        self.on_play()

        Clock.schedule_interval(self._check_sound_finished, 0.1)


    def _check_sound_finished(self, dt):
        if self.sound.state == "stop":
            self._update_ui(True, can_retry=False, can_start=False)
            self._start_timer()

            return False


    def playback(self):
        if not self.current_filepath:
            return

        self.sound = SoundLoader.load(self.current_filepath)

        if self.sound is None:
            self.status_text = "Could not load audio."
            return

        self.sound.play()

        return True

    def on_play(self):
        if not self.current_filepath:
            self.status_text = "No audio loaded yet."
            return

        self.status_text = "Playing audio..."
        success = self.playback()

        if not success:
            self.status_text = "Could not play audio on this device."
        else:
            self.status_text = "Audio playing."

    def on_guess(self, language_code):
        lang_types = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
        }

        if not self.current_language:
            self.status_text = "Load a sentence first."
            return

        self._stop_timer()
        full_lang_text = lang_types.get(self.current_language, self.current_language)

        if language_code == self.current_language:
            earned = max(0, 10 * self.time_left)
            self.score += earned
            self.loops += 1
            self.feedback_text = f"Correct! The language was {full_lang_text}. +{earned} points."
            self.status_text = f"Loading next sentence in 5 seconds..."

            self._update_ui(False, can_retry=False, can_start=False)
            Clock.schedule_once(self.load_sentence, 5)
        else:
            self.feedback_text = f"Incorrect. The correct language is {full_lang_text}."
            self.status_text = f"Sentence: {self.current_sentence}"

            self._update_ui(False, can_retry=True, can_start=False)

    def on_retry(self):
        self.reset_game()

    def reset_game(self):
        self._stop_timer()

        self.current_sentence = ""
        self.current_language = ""
        self.current_filepath = ""
        self.sentence_text = "Press START to load a sentence."
        self.language_code = ""
        self.feedback_text = "Choose the language after listening."
        self.status_text = "Ready"
        self.score = 0
        self.loops = 0

        self._update_ui(False, can_retry=False, can_start=True)


class GTTSApp(App):
    def build(self):
        return GTTSGame()


if __name__ == "__main__":
    GTTSApp().run()
