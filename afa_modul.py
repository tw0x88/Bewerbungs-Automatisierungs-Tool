"""
Dateiname: afa_modul.py
Autor: Manuel Kilzer
Datum: 08. Oktober 2024

Beschreibung:
    Dieses Modul ist für die durchsuchung der Stellenbörse der Agentur für Arbeit nach passenden Ausbildungsbetrieben verantwortlich.

Copyright (c) 2024 Manuel Kilzer
"""

# Standardbibliotheken
import time
import re

# Drittanbieter-Bibliotheken
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# Klasse für Stellenanzeigen der Agentur für Arbeit
class Stellenanzeige():
    def __init__(self, linkAfA, driver, gpt_Ansprechpartner, gpt_Geschlecht):
        self.driver = driver # der Selenium Webdriver zur steuerung des Browsers. 
        self.gpt_Ansprechpartner = gpt_Ansprechpartner
        self.gpt_Geschlecht = gpt_Geschlecht

        self.stellenTyp = None
        self.stellenName = None
        self.stellenBeschreibung = None
        self.arbeitgeberName = None 
        self.emailAdresse = None
        self.ansprechpartner = None
        self.ansprechpartnerAnsprache = None
        self.linkWebseite = None
        self.linkStellenAbgebot = linkAfA
        self.ort = None
        self.arbeitsOrt = None
        self.strasseHnr = None
        self.plzStadt = None
        self.mindAbschluss = None
        self.afaReferenzNr = None

        print("=====================================================================================")
        print("Stellenangebot Link:", self.linkStellenAbgebot)

    def set_stellenTyp(self):
        try:
            self.stellenTyp = self.driver.find_element("id", "detail-kopfbereich-angebotsart").text
            print("Stellen-Typ:", self.stellenTyp)

        except Exception as error:
            print("Stellen-Typ: Keine Daten.")

    def set_stellenName(self):
        try:
            self.stellenName = self.driver.find_element("id", "detail-kopfbereich-titel").text
            print("Stellen-Name:", self.stellenName)

        except Exception as error:
            print("Stellen-Name: Keine Daten.")

    def set_stellenBeschreibung(self):
        try:
            self.stellenBeschreibung = self.driver.find_element("id", "detail-beschreibung-beschreibung").text
            print("Stellen-Beschreibung:", self.stellenBeschreibung)
            print()

        except Exception as error:
            print("Stellen-Beschreibung: Keine Daten.")
        
    def set_arbeitgeberName(self):
        try:
            self.arbeitgeberName = self.driver.find_element("id", "detail-kopfbereich-firma").text
            print("Arbeitgeber-Name:", self.arbeitgeberName)

        except Exception as error:
            print("Arbeitgeber-Name: Keine Daten.")

    def set_linkWebseite(self):
        try:
            self.linkWebseite = self.driver.find_element("id", "detail-agdarstellung-link-0").get_attribute("href")
            print("Weblink:", self.linkWebseite)

        except Exception as error:
            print("Weblink: Keine Daten.")

    # Auslesen des angegebenen Arbeitsorts aus dem Stellenangebot und zuweisung zur ort Variable.
    def set_ort(self):
        try:
            self.ort = self.driver.find_element("id", "detail-kopfbereich-arbeitsort").text
            print("Arbeits-Ort:", self.ort)

        except Exception as error:
            print("Arbeits-Ort: Keine Daten.")

    def set_arbeitsOrt(self):
        try:
            self.arbeitsOrt = self.driver.find_element("id", "detail-arbeitsorte-arbeitsort-0").text
            print("Arbeits-Adresse:", self.arbeitsOrt)

        except Exception as error:
            print("Arbeits-Adresse: Keine Daten.")

    def set_mindAbschluss(self):
        try:
            abschluss = self.driver.find_element("id", "detail-beschreibung-bildungsabschluss").text.replace("Benötigter Schulabschluss: ", "")
            if "hauptschul" in abschluss.lower():
                self.mindAbschluss = 1

            elif "mittlere" in abschluss.lower():
                self.mindAbschluss = 2

            elif "fachhochschul" in abschluss.lower():
                self.mindAbschluss = 3

            print("Geforderter Abschluss:", lesbareAbschluesse_dict[self.mindAbschluss])

        except Exception as error:
            print("Geforderter Abschluss: Keine Daten.")

    def set_afaReferenzNr(self):
        try:
            self.afaReferenzNr = self.driver.find_element("id", "detail-footer-referenznummer").text
            print("Referenz-Nr.:", self.afaReferenzNr)

        except Exception as error:
            print("Referenz-Nr.: Keine Daten.")

    def search_emailAdresse(self):
        try:
            print("Suche Emailadresse.")
            emailPattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            email_matches = re.findall(emailPattern, self.stellenBeschreibung)
            if len(email_matches) >= 1:
                self.emailAdresse = email_matches[0]
            else:
                self.emailAdresse = None

            print("Email:", self.emailAdresse)

        except Exception as error:
            print("Email: Keine Daten.")

    def search_ansprechpartner(self):
        try:
            print("Suche Ansprechpartner.")
            # Dieses RegEx-Muster selektiert Anreden ("Frau" oder "Herr/Herrn") und kann bis zu drei Namen erfassen.
            # Es wird verwendet, um mögliche Ansprechpartner im Text zu identifizieren. In seltenen Fällen sind andere
            # Namen im Text zu finden, was zu einer möglichen falschen Ansprache der Bezugsperson führen kann, an die die 
            # Bewerbung gehen soll. Sollte mit RegEx kein Name gefunden werden, wird versucht, mit GPT einen Namen heraus-
            # zu filtern.
            ansprechPattern = r"(Frau|Herrn?)\s(([A-Z][a-z]+)(\s[A-Z][a-z]+)?(\s[A-Z][a-z]+)?)"

            if self.stellenBeschreibung:
                if self.emailAdresse:
                    re_ergebnis = re.search(ansprechPattern, self.stellenBeschreibung)

                    if re_ergebnis:
                        if "fr" in re_ergebnis.group(1).lower():
                            self.ansprechpartnerAnsprache = "Frau"

                        elif "he" in re_ergebnis.group(1).lower():
                            self.ansprechpartnerAnsprache = "Herr"

                        self.ansprechpartner = re_ergebnis.group(2)

                    else:
                        ansprechpartner_Antwort = self.gpt_Ansprechpartner.fragen(self.stellenBeschreibung.replace("\n", " ")).replace(".", "").replace(",", "")
                        print("Ansprechpartner GPT:", ansprechpartner_Antwort)

                        if ansprechpartner_Antwort != "None":
                            self.ansprechpartner = ansprechpartner_Antwort
                            geschlecht_Antwort = self.gpt_Geschlecht.fragen(self.ansprechpartner).replace(".", "").replace(",", "")
                            print("Geschlecht GPT:", geschlecht_Antwort)

                            if geschlecht_Antwort != "None":
                                self.ansprechpartnerAnsprache = geschlecht_Antwort

                    if self.ansprechpartner != None:
                        self.ansprechpartner = self.ansprechpartner.replace("\n", "")

                    if self.ansprechpartnerAnsprache != None:
                        self.ansprechpartnerAnsprache = self.ansprechpartnerAnsprache.replace("\n", "")

            print("Ansprechpartner:", self.ansprechpartner)
            print("Ansprechpartner Geschlecht:", self.ansprechpartnerAnsprache)

        except Exception as error:
            print("Ansprechpartner: Keine Daten.")

    # Funktion zerlegt den String in self.arbeitsOrt in mögliche einzel Strings mit Straße und Hausnummer // PLZ und Stadtname
    # und speichert diese in self.strasseHnr und self.pltStadt
    def adresse_zerlegen(self):
        print("Löse Adresse in Bestandteile auf.")
        try:
            if self.arbeitsOrt != None:
                if "," in self.arbeitsOrt:
                    adressList = self.arbeitsOrt.split(", ")
                    self.strasseHnr = adressList[0]
                    self.plzStadt = adressList[1]

                else:
                    self.plzStadt = self.arbeitsOrt

        except Exception as error:
            print("adresse_zerlegen Fehler!", error)

    def set_AlleDaten(self):
        self.set_stellenTyp()
        self.set_stellenName()
        self.set_stellenBeschreibung()
        self.set_arbeitgeberName()
        self.set_linkWebseite()
        self.set_ort()
        self.set_arbeitsOrt()
        self.set_mindAbschluss()
        self.set_afaReferenzNr()
        self.search_emailAdresse()
        self.search_ansprechpartner()
        self.adresse_zerlegen()

# Funktion zum Entfernen des Cookie-Fensters der Webseite.
def entferneCookieFenster(driver):
    print("Entferne Cookie-Fenster")
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER)
    actions.perform()

# Funktion zum Wechseln zur Ausbildungssuche in der Suchmaske.
def wechsleZurAusbildungsSuche(driver):
    print("Wechsle von der Arbeitssuche zur Ausbildungssuche.")
    dropdownAuswahl = driver.find_element("id", "Angebotsart-dropdown-button")
    dropdownAuswahl.click()
    time.sleep(1)
    auswahlAusbildungen = driver.find_element("id", "Angebotsart-dropdown-item-1")
    auswahlAusbildungen.click()

# Funktion gibt in die Suchmaske ein WAS gesucht wird.
def wasEingabe(driver, text):
    print("Gib den zu suchenden Jobtitel in die Maske ein.")
    was = driver.find_element("id", "was-input")
    was.send_keys(text)

# Funktion gibt in die Suchmaske ein WO gesucht wird.
def woEingabe(driver, text):
    print("Gib die Postleitzahl in die Maske ein.")
    wo = driver.find_element("id", "wo-input")
    wo.send_keys(text)

# Funktion klickt in der Suchmaske auf den "Stellen finden" Button und löst somit die Suche aus.
def stellenFindenClick(driver):
    print("Klicke auf den Button -Stellen Finden-.")
    findenButton = driver.find_element("id", "btn-stellen-finden")
    findenButton.click()

# Funktion definiert den Ablauf der Eingabe der Daten für WAS und WO.
def sucheNachAusbildungsstellen(driver, was, wo):
    wasEingabe(driver, was)
    time.sleep(1)
    woEingabe(driver, wo)
    time.sleep(1)
    stellenFindenClick(driver)

# Funktion wechselt die Ansicht der angezeigten Suchergebnisse zur Listenansicht.
def wechsleZurListenAnsicht(driver):
    print("Wechsle die Ergebnisansicht zur Listenansicht.")
    listenAnsichtButton = driver.find_element("id", "listen-layout-button")
    listenAnsichtButton.click()

# Funktion sortiert die Suchergebnisse nach Entfernung.
def wechsleSortierungNachEntfernung(driver):
    print("Sortiere die Ergebnisse nach Entfernung.")
    dropDownSortierung = driver.find_element("id", "sortierung-dropdown-button")
    dropDownSortierung.click()
    time.sleep(0.5)
    entfernungButton = driver.find_element("id", "sortierung-dropdown-item-4")
    entfernungButton.click()
    time.sleep(0.5)

# Die Funktion scrollt 6 Mal nach unten, um an den unteren Bildrand zu kommen, wo der Link zum Laden weiterer Ergebnisse
# ist. Danach werden alle Links der Stellenangebote ausgelesen und in einer Liste (links = []) gespeichert.
# Sie gibt in der Konsole aus, wie viele Links sie insgesamt gefunden hat. Zurückgegeben wird die liste (links).
def fetchResultLinks(driver):
    print("Lade alle Stellenanzeigen-Links in das Programm.")
    for x in range(6):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scrolle runter.
            print("Scroll down.")
            time.sleep(1)
            weitereErgebnisseButton = driver.find_element("id", "ergebnisliste-ladeweitere-button")

            if weitereErgebnisseButton:
                weitereErgebnisseButton.click()

            time.sleep(1)

        except Exception as error:
            # Bei dieser Exception soll nichts weiter passieren wenn sie fällt. 
            # Ist einfach nur wenn bereits ganz nach unten gescrollt wurde.
            pass
    
    quellText = driver.page_source
    ergebnisse_count = quellText.lower().count("ergebnisliste-item".lower()) # Zählt die Links.

    links = []
    count = 0
    for x in range(ergebnisse_count):
        try:
            href = driver.find_element("id", "ergebnisliste-item-" + str(count)).get_attribute("href") # Lese Link aus.
            links.append(href) # Füge Link der liste links hinzu.
            count += 1

        except Exception as error:
            # Sollte der driver das Element nicht finden können.
            break

    print()
    print("Es wurden", len(links), "Stellenanzeigen-Links der Agentur für Arbeit geladen.")
    return links

# DICTIONARYS
# Dict das Integer (1-3) in Schulabschlüsse umwandelt.
lesbareAbschluesse_dict = {1 : "Hauptschulabschluss", 2 : "Mittlere Reife", 3 : "Fachhochschulreife"}