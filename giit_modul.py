"""
Dateiname: giit_modul.py
Autor: Manuel Kilzer
Datum: 08. Oktober 2024

Beschreibung:
    Dieses Modul ist für die durchsuchung der Stellenbörse von get-in-it.de nach passenden Betrieben verantwortlich.
    Diese Webseite ist nicht für Ausbildungsstellen geeignet.

Copyright (c) 2024 Manuel Kilzer
"""

# Standardbibliotheken
import time
import re

# Klasse für Stellenanzeigen
class Stellenanzeige():
    def __init__(self, linkGiit):
        #self.driver = driver # der Selenium Webdriver zur steuerung des Browsers. 

        self.linkStellenAbgebot = linkGiit
        self.stellenName = None
        self.stellenBeschreibung = None
        self.arbeitgeberName = None 
        self.emailAdresse = None
        self.strasseHnr = None
        self.plzStadt = None

        print("=====================================================================================")

    def set_stellenName(self, stellenName):
        self.stellenName = stellenName

    def set_stellenBeschreibung(self, stellenBeschreibung):
        self.stellenBeschreibung = stellenBeschreibung

    def set_arbeitgeberName(self, arbeitgeberName):
        self.arbeitgeberName = arbeitgeberName

    def set_emailAdresse(self, emailAdresse):
        self.emailAdresse = emailAdresse

    def set_emailAdresse(self, emailAdresse):
        self.emailAdresse = emailAdresse

    def set_strasseHnr(self, strasseHnr):
        self.strasseHnr = strasseHnr

    def set_plzStadt(self, plzStadt):
        self.plzStadt = plzStadt

# Funktion zum Entfernen des Cookie-Fensters der Webseite.
def entferneCookieFenster(driver):
    coockieButton = driver.find_element("class name", "CookieConsentMainScreen_saveAll__vfuUP")
    coockieButton.click()

# Die Funktion scrollt solange nach unten, um an den unteren Bildrand zu kommen, wo der Link zum Laden weiterer Ergebnisse
# ist. Danach werden alle Links der Stellenangebote ausgelesen und in einer Liste (links = []) gespeichert.
# Sie gibt in der Konsole aus, wie viele Links sie insgesamt gefunden hat. Zurückgegeben wird die liste (links).
def fetchResultLinks(driver):
    print("Lade alle Stellenanzeigen-Links in das Programm.")
    angezeigteStellenAnzahl = int(driver.find_element("css selector", ".JobSearchJobs_headline__P94n5 > span:nth-child(1)").text)
    anzahlJobCards = len(driver.find_elements("class name", "CardJob_jobCard__KgSk0"))
    while anzahlJobCards < angezeigteStellenAnzahl:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scrolle runter.
            print("Scroll down.")
            time.sleep(1)
            closeRegWindow = driver.find_element("class name", "RegisterFlag_close__AvqcV")

            if closeRegWindow:
                closeRegWindow.click()

            time.sleep(1)
            mehr_laden_button = driver.find_element("class name", "btn-primary-inverted")

            if mehr_laden_button:
                mehr_laden_button.click()

            time.sleep(1)

            anzahlJobCards = len(driver.find_elements("class name", "CardJob_jobCard__KgSk0"))
            print("Aktuell geladene Links:", anzahlJobCards, "/", angezeigteStellenAnzahl)

        except Exception as error:
            break

    jobCards = driver.find_elements("class name", "CardJob_jobCard__KgSk0")
    print("JobCards:", len(jobCards))

    links = []
    for card in jobCards:
        link = card.get_attribute("href")
        links.append(link)

    print()
    return links