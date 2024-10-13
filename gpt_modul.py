"""
Dateiname: gpt_modul.py
Autor: Manuel Kilzer
Datum: 08. Oktober 2024

Beschreibung:
    Dieses Modul stellt die Funktionen für die Kommunikation mit der OpenAI-API zur verfügung. 

Copyright (c) 2024 Manuel Kilzer
"""

# Drittanbieter-Bibliotheken
import openai

# Klasse für den Chat mit OpenAI
class GPT_API:
    def __init__(self, api_key, rolle):
        openai.api_key = api_key
        self.dialog = [{"role" : "system", "content" : rolle}]

    def fragen(self, frage):
        self.dialog.append({"role" : "user", "content" : frage})
        response = openai.chat.completions.create(model = "gpt-3.5-turbo", messages = self.dialog)
        antwort = response.choices[0].message.content
        self.dialog.append({"role" : "assistant", "content" : antwort})
        return antwort