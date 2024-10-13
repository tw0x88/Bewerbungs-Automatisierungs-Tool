"""
Dateiname: xing_modul.py
Autor: Manuel Kilzer
Datum: 08. Oktober 2024

Beschreibung:
    Dieses Modul ist für die durchsuchung der Stellenbörse von Xing nach passenden Ausbildungsbetrieben verantwortlich.

Copyright (c) 2024 Manuel Kilzer
"""

# Standardbibliotheken
import time
import os

# Drittanbieter-Bibliotheken
from selenium.webdriver.firefox.options import Options
from selenium import webdriver


XING = "https://www.xing.com/jobs/search?sc_o=jobs_search_button&keywords=Fachinformatiker%20Anwendungsentwicklung&location=Stuttgart&radius=20&id=caa21e8e138c163e59f5fa489afa2cef&careerLevel=1.795d28"


