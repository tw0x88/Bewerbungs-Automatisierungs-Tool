"""
Dateiname: main.py
Autor: Manuel Kilzer
Datum: 20. September 2024

Beschreibung:
    Dieses Skript automatisiert die Suche, filterung und Bewerbung für Stellenanzeigen für Fachinformatiker in Anwendungsentwicklung auf der Webseite der Arbeitsagentur. 
    Es durchsucht die Website gezielt nach Stellenangeboten, die den spezifischen Vorgaben und Kriterien entsprechen. Dabei extrahiert es relevante Informationen 
    wie Stellenbeschreibungen, Arbeitsort und Kontaktdaten von potenziellen Arbeitgebern. Nach der Extraktion filtert das Skript die gefundenen Stellenanzeigen 
    nach vordefinierten Kriterien und sendet dann automatisch Bewerbungen per E-Mail an die entsprechenden Arbeitgeber.

Abhängigkeiten:
    - geckodriver.exe (für Selenium mit Firefox) https://github.com/mozilla/geckodriver/releases
    - firefox.exe https://www.mozilla.org/de/firefox/

Copyright (c) 2024 Manuel Kilzer
"""

# TODO:
# AB Test der Bewerbung!!!

# Standardbibliotheken
import configparser
import time
import csv
import os
import re

# Drittanbieter-Bibliotheken
from selenium.webdriver.firefox.options import Options
from selenium import webdriver

# Benutzerdefinierte Module
import emaildaten as mailData
import smtp_modul as smtpM
import giit_modul as giitM
#import xing_modul as xingM
import gpt_modul as gptM
import pdf_modul as pdfM
import afa_modul as afaM

# KONSTANTEN
# Dateipfad zur CSV-Datei in der die Frimennamen und Email-Adressen gespeichert sind/werden bei denen sich schon Beworben wurde.
CSV_DATEIPFAD = "firmenspeicher.csv"

# Dateipfad zur INI.Datei mit Einstellungen, Konfigurationen und Listen.
INI_DATEIPFAD = "config.ini"

# Links zu den Stellenbörsen
GET_IN_IT = "https://www.get-in-it.de/jobsuche?thematicPriority=36&city=1047&radius=10"
ARBEITSAGENTUR_STELLEN = "https://www.arbeitsagentur.de/jobsuche/suche"

# DICTIONARYS
# Dict das Integer (1-12) in Monatsnamen umwandelt.
monat_dict = {1 : "Januar",
              2 : "Februar",
              3 : "März",
              4 : "April",
              5 : "Mai",
              6 : "Juni",
              7 : "Juli",
              8 : "August",
              9 : "September",
              10 : "Oktober",
              11 : "November",
              12 : "Dezember"
              }

#VARIABLEN
driver = None

datum_anschreiben = time.strftime("Stuttgart, den %d.%m.%Y")
lebenslauf_monat = monat_dict[int(time.strftime("%m"))]
datum_lebenslauf = time.strftime("Stuttgart, den %d. ") + lebenslauf_monat + time.strftime(" %Y")

anschreiben_pdf = "pdf_work\\anschreiben.pdf"
overlay_anschreiben_pdf = "pdf_work\\overlay_anschreiben.pdf"    
output_anschreiben_pdf = "pdf_work\\output_anschreiben.pdf"

lebenslauf_pdf = "pdf_work\\lebenslauf.pdf"
overlay_lebenslauf_pdf = "pdf_work\\overlay_lebenslauf.pdf"
output_lebenslauf_pdf = "pdf_work\\output_lebenslauf.pdf"

if __name__ == "__main__":
    os.system("cls") # Leeren der Konsolenausgabe

    # Lade Voreinstellungen und Daten aus config.ini
    if os.path.exists(INI_DATEIPFAD):
        configINI = configparser.ConfigParser()
        configINI.read(INI_DATEIPFAD, encoding = "utf-8")

        # Die Variable TESTMODUS regelt ob das Program im Scharfen- oder im Testmodus läuft.
        # Im Testmodus gehen die Emails an eine fest definierte Emailadresse anstatt an die Firmen.
        TESTMODUS = configINI.getboolean("test", "testmodus")
        TESTEMAIL = configINI["test"]["email"]
        
        # Die _GO Variablen regeln welche Programmabschnitte durchlaufen werden sollen.
        # Abschnitte werden nur bei -True- durchlaufen.
        afa_GO = configINI.getboolean("programmabschnitt", "afa_GO")
        giit_GO = configINI.getboolean("programmabschnitt", "giit_GO")

        # Die Variabble HEADLESS regelt ob der Firefox Browser angezeigt werden soll.
        # Wenn -False- kann man der Interaktion zusehen.
        HEADLESS = configINI.getboolean("browser", "headless")

        # Liste von Firmen bei denen sich nicht beworben werden soll.
        blacklist_Firmen = configINI["blacklist"]["firmen"].split(", ")

        # Liste mit Wörtern die eine Bewerbung ausschlissen sollen.
        blacklist_Words = configINI["blacklist"]["words"].split(", ")

        # SMTP Credentials werden hier aus der .ini geladen
        smtpEmail = configINI["smtp"]["email"]
        smtpPw = configINI["smtp"]["pw"]

        gptKey = configINI["gpt"]["key"]
        gptRolleAnsprechpartner = configINI["gpt"]["rolle_Ansprechpartner"]
        gptRolleGeschlecht = configINI["gpt"]["rolle_Geschlecht"]

    else:
        print(f"Die Datei {INI_DATEIPFAD} existiert nicht.")
        time.sleep(1)
        exit()

    if os.path.exists(CSV_DATEIPFAD):
        with open(CSV_DATEIPFAD, mode='r', newline='', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            liste_Firmen = [zeile[0] for zeile in reader]

    else:
        print(f"Die Datei {CSV_DATEIPFAD} existiert nicht.")
        time.sleep(1)
        exit()
    
    if TESTMODUS == False:
        os.system("color 4") # Konsolenschriftfarbe wird auf Rot gesetzt.
        print("TESTMODUS ist AUS!")
        print("ACHTUNG! Es werden Bewerbungen an FIRMEN versandt!!")
        userEingabe = input("Bestätige mit Enter wenn das so gewollt ist oder sende 'x' für Exit.  ")
        if userEingabe.lower() == "x":
            exit()

    else:
        os.system("color A") # Konsolenschriftfarbe wird auf Grün gesetzt.
        print("TESTMODUS ist AN.")
    
    try:
        gpt_Ansprechpartner = gptM.GPT_API(gptKey, gptRolleAnsprechpartner) # Speziell auf ermittlung von Ansprechpartnern getrimmte GPT-Prompts.
        gpt_Geschlecht = gptM.GPT_API(gptKey, gptRolleGeschlecht) # Speziell auf Ermittlung der Anspsprache (Geschlecht) getrimmte GPT-Prompts.

        optionen = Options()
        if HEADLESS == True:
            optionen.add_argument("--headless")  # Den Headless-Mode von Firefox aktivieren

        driver = webdriver.Firefox(options = optionen) # Starte Firefox
        driver.set_window_position(10, 10) # Position des Browserfensters im Hauptbildschirm von oben links
        driver.set_window_size(1500, 1100) # bxh

        ######################################################################################
        ############################### Agentur für Arbeit ###################################
        ######################################################################################

        if afa_GO == True:
            # Alle Links der Stellenangebote der Agentur für Arbeit crawlen.
            driver.get(ARBEITSAGENTUR_STELLEN)
            time.sleep(4)
            afaM.entferneCookieFenster(driver)
            time.sleep(2)
            afaM.wechsleZurAusbildungsSuche(driver)
            time.sleep(1)
            afaM.sucheNachAusbildungsstellen(driver, "Fachinformatiker Anwendungsentwicklung", "70565")
            time.sleep(1)
            afaM.wechsleZurListenAnsicht(driver)
            time.sleep(0.5)
            links = afaM.fetchResultLinks(driver)

            # Alle Stellenanzeigen der Agentur für Arbeit crawlen
            afa_stellenangebote = []
            for link in links:
                driver.get(link)
                time.sleep(2)

                afa_stellenangebot = afaM.Stellenanzeige(link, driver, gpt_Ansprechpartner, gpt_Geschlecht)
                afa_stellenangebot.set_AlleDaten()
                if afa_stellenangebot.emailAdresse != None: # Füge Stellenangebot nur hinzu wenn eine Emailadresse enthalten ist.
                    afa_stellenangebote.append(afa_stellenangebot)
                
            print("Es sind", len(afa_stellenangebote), "mit angegebener Email-Adresse.")
            print()

            # Hier werden die Stellenangebote darauf überprüft ob bereits schon Bewerbungen an diese raus sind.
            # Ebenfalls wird überprüft ob die Firmen in einer Liste sind, an die keine Bewerbungen raus sollen.
            for afa_stelle in afa_stellenangebote:
                if afa_stelle.emailAdresse not in liste_Firmen and afa_stelle.arbeitgeberName not in liste_Firmen: # Überprüft ob Firma oder E-Mail bereits angeschrieben wurde.
                    block = False
                    for word in blacklist_Words:
                        if word in afa_stelle.stellenBeschreibung.lower():
                            block = True
                            print("============================================")
                            print("## BLOCK Wort ##", word)

                    for firma in blacklist_Firmen:
                        if firma in afa_stelle.arbeitgeberName.lower() or firma in afa_stelle.stellenBeschreibung.lower(): # Prüfung ob Firma unerwünscht ist.
                            block = True
                            print("============================================")
                            print("## BLOCK Firma ##", firma)

                    if block != True:
                        print("============================================")
                        print("Firmenname:", afa_stelle.arbeitgeberName)
                        print("E-Mailadresse:", afa_stelle.emailAdresse)

                        # Überprüfen ob ein Ansprechpartner gefunden wurde und eine passende Ansprache dazu.
                        if afa_stelle.ansprechpartner != None or afa_stelle.ansprechpartnerAnsprache != None:
                            # Konstruieren des Ansprachenblocks (Beispiel: Herr Max Mustermann)
                            gesamtAnsprechpartner = afa_stelle.ansprechpartnerAnsprache + " " + afa_stelle.ansprechpartner

                            # Konstruieren des Ansprachensatzes
                            if "Herr" in afa_stelle.ansprechpartnerAnsprache:
                                gesamtAnsprache = "Sehr geehrter " + gesamtAnsprechpartner + ","
                            
                            elif "Frau" in afa_stelle.ansprechpartnerAnsprache:
                                gesamtAnsprache = "Sehr geehrte " + gesamtAnsprechpartner + ","
                            
                            else:
                                gesamtAnsprache = "Sehr geehrte Damen und Herren,"

                            print("Ansprache:", gesamtAnsprache)

                        else:
                            gesamtAnsprache = "Sehr geehrte Damen und Herren,"
                            print("Ansprache:", gesamtAnsprache)

                        # Konstruieren der Anschrift
                        if afa_stelle.ansprechpartner != None or afa_stelle.ansprechpartnerAnsprache != None:
                            if afa_stelle.strasseHnr != None:
                                bewerbungAnschrift = afa_stelle.arbeitgeberName + "\n" + "z. Hd. " + afa_stelle.ansprechpartnerAnsprache + " " + afa_stelle.ansprechpartner + "\n" + afa_stelle.strasseHnr + "\n\n" + afa_stelle.plzStadt

                            else:
                                bewerbungAnschrift = afa_stelle.arbeitgeberName + "\n" + "z. Hd. " + afa_stelle.ansprechpartnerAnsprache + " " + afa_stelle.ansprechpartner + "\n\n" + afa_stelle.plzStadt

                        else:
                            if afa_stelle.strasseHnr != None:
                                bewerbungAnschrift = afa_stelle.arbeitgeberName + "\n" + afa_stelle.strasseHnr + "\n\n" + afa_stelle.plzStadt
                            
                            else:
                                bewerbungAnschrift = afa_stelle.arbeitgeberName + "\n\n" + afa_stelle.plzStadt

                        print()
                        print("Bewerbungsanschrift:")
                        print()
                        print(bewerbungAnschrift)
                        print()

                        # Konstruieren der E-Mail
                        if TESTMODUS == True:
                            emailAdresse = TESTEMAIL # Email zu Testzwecken

                        else:
                            emailAdresse = afa_stelle.emailAdresse
                        
                        emailBetreff = mailData.emailBetreff
                        emailGesamtText = gesamtAnsprache + "\n\n" + mailData.emailText.replace("\t", "")

                        # Konstuieren des Bewerbungs-PDFs / Anhangs
                        pdfM.create_anschreiben_overlay(bewerbungAnschrift, datum_anschreiben, gesamtAnsprache, overlay_anschreiben_pdf)
                        pdfM.merge_pdfs(anschreiben_pdf, overlay_anschreiben_pdf, output_anschreiben_pdf)
                        print(f"Anschreiben PDF wurde erstellt: {output_anschreiben_pdf}")

                        pdfM.create_lebenslauf_overlay(datum_lebenslauf, overlay_lebenslauf_pdf)
                        pdfM.merge_pdfs(lebenslauf_pdf, overlay_lebenslauf_pdf, output_lebenslauf_pdf)
                        print(f"Lebenslauf PDF wurde erstellt: {output_lebenslauf_pdf}")

                        # Overlay-Dateien löschen, da sie nicht mehr benötigt werden
                        time.sleep(1.5)
                        if os.path.exists(overlay_anschreiben_pdf):
                            os.remove(overlay_anschreiben_pdf)
                            print(f"Overlay-Datei '{overlay_anschreiben_pdf}' wurde gelöscht")

                        if os.path.exists(overlay_lebenslauf_pdf):
                            os.remove(overlay_lebenslauf_pdf)
                            print(f"Overlay-Datei '{overlay_lebenslauf_pdf}' wurde gelöscht")

                        # Erstelle die finale PDF-Datei für die Bewerbung
                        pdfs = ["pdf_work\\output_anschreiben.pdf", "pdf_work\\output_lebenslauf.pdf", "pdf_work\\zeugnisse.pdf", "pdf_work\\Infoblatt_Praktikumsbetriebe_GFN.pdf"]
                        output_pdf_path = "Bewerbung als Praktikant Fachinformatiker Anwendungsentwicklung von Manuel Kilzer.pdf"
                        safe_output_pdf_path = "pdf_safe\\Bewerbung " + afa_stelle.arbeitgeberName + time.strftime(" %d_%m_%Y") + "_afa.pdf"
                        pdfM.make_final_pdf(pdfs, output_pdf_path)

                        if TESTMODUS != True: # Gesichterte PDFs nur von wirklich verschickten Bewerbungen.
                            pdfM.make_final_pdf(pdfs, safe_output_pdf_path)

                        print("Die PDFs wurden erfolgreich zusammengefügt.")

                        # Output-Dateien löschen, da sie nicht mehr benötigt werden
                        time.sleep(1.5)
                        if os.path.exists(output_anschreiben_pdf):
                            os.remove(output_anschreiben_pdf)
                            print(f"Output-Datei '{output_anschreiben_pdf}' wurde gelöscht")

                        if os.path.exists(output_lebenslauf_pdf):
                            os.remove(output_lebenslauf_pdf)
                            print(f"Output-Datei '{output_lebenslauf_pdf}' wurde gelöscht")

                        emailAnhang = "Bewerbung als Praktikant Fachinformatiker Anwendungsentwicklung von Manuel Kilzer.pdf"
                        
                        # Versende E-Mail und füge Firma der Liste (liste_Firmen) hinzu um doppelte E-Mails zu vermeiden.
                        smtpM.send_email(smtpEmail, smtpPw, emailAdresse, emailBetreff, emailGesamtText, emailAnhang)

                        # Füge aktuelle Firma der Firmenliste hinzu bei denen sich schon beworben wurde.
                        liste_Firmen.extend([afa_stelle.arbeitgeberName, afa_stelle.emailAdresse])
                        time.sleep(1.5)

                        # Lösche die bereits gesendete PDF-Datei
                        if os.path.exists(output_pdf_path):
                            os.remove(output_pdf_path)
                            print(f"Bewerbung '{output_pdf_path}' wurde gelöscht.")

                        time.sleep(1.5)

                        # Eine Iteration reicht zum Testen.
                        if TESTMODUS == True:
                            break

                else:
                    print("============================================")
                    print("## BLOCK Firma ## Bereits beworben.")

                print()
                print()

        ######################################################################################
        #################################### get-in-IT #######################################
        ######################################################################################

        if giit_GO == True:
            # Alle Links der Stellenangebote von get-in-it crawlen.
            driver.get(GET_IN_IT)
            time.sleep(4)
            giitM.entferneCookieFenster(driver)
            time.sleep(2)
            links = giitM.fetchResultLinks(driver)

            arbeitgeber_Liste = []
            linkCounter = 1
            for link in links:
                print("Link:", linkCounter, "/", len(links))
                linkCounter += 1
                driver.get(link)
                time.sleep(3)
                arbeitgeberKurzName = driver.find_elements("class name", "link-text")[1].text
                jobTitel = driver.find_element("class name", "JobHeaderRegular_jobTitle__DS4V4").text
                gesamtText = driver.find_element("class name", "JobDescription_jobDescription__i216P").text

                strasseHnr = None
                plzStadt = None
                emailAdresse = None
                arbeitgeberName = None

                if arbeitgeberKurzName not in arbeitgeber_Liste:
                    try:
                        mehrStandorteAnzeigenButton = driver.find_element("class name", "JobHeaderRegular_moreItems__z3tVf").click()
                        time.sleep(0.2)
                        standorte = driver.find_element("class name", "JobHeaderRegular_jobLocation__MFauy").text
                        gesamtText += "\n"
                        gesamtText += standorte
                        gesamtText += "\n"            
                    except:
                        pass

                    giit_stelle = giitM.Stellenanzeige(link)
                    arbeitgeber_Liste.append(arbeitgeberKurzName)

                    arbeitgeber_Profil_Link = driver.find_element("link text", "Profil").get_attribute("href")
                    driver.get(arbeitgeber_Profil_Link)
                    time.sleep(3)

                    try:
                        kontakt_txtFeld = driver.find_element("class name", "TopContact_body__A5gdB").text
                        gesamtText += kontakt_txtFeld
                        gesamtText += "\n"
                    except:
                        pass

                    try:
                        datenUndFakten_txtFeld = driver.find_element("class name", "TopFact_facts__N3L5P").text
                        gesamtText += datenUndFakten_txtFeld
                        gesamtText += "\n"
                    except:
                        pass

                    try:
                        arbeitgeberName = driver.find_element("css selector", "div.mb-1:nth-child(2)").text
                    except:
                        pass

                    try:
                        adresse = driver.find_element("css selector", ".TopContact_body__A5gdB > div:nth-child(3) > div:nth-child(1)").text
                        teileAdresse = adresse.split("\n")

                        if "str" in teileAdresse[0].lower():
                            strasseHnr = teileAdresse[0]

                        else:
                            strasseHnr = None
                        
                        if re.search(r'\b\d{5}\b', teileAdresse[1]):
                            plzStadt = teileAdresse[1]

                        else:
                            plzStadt = None

                    except:
                        strasseHnr = None
                        plzStadt = None

                    try:
                        emailAdresse = driver.find_element("class name", "TopContact_infoEmail__mk_61").get_attribute("href").replace("mailto:", "")
                    except:
                        pass

                    print("==========================================")
                    print("Arbeitgeber (Kurz):", arbeitgeberKurzName)
                    print("Arbeitgeber (Lang):", arbeitgeberName)
                    print("Stellenbezeichnung:", jobTitel)
                    print("Stellenbeschreibung:")
                    print(gesamtText)
                    print("Straße Hausnummer:", strasseHnr)
                    print("PLZ Stadt:", plzStadt)
                    print("Email-Adresse:", emailAdresse)
                    print()
                    print()

                    giit_stelle.set_stellenName(jobTitel)
                    giit_stelle.set_stellenBeschreibung(gesamtText)
                    giit_stelle.set_arbeitgeberName(arbeitgeberName)
                    if emailAdresse != None:
                        giit_stelle.set_emailAdresse(emailAdresse.lower())
                    giit_stelle.set_strasseHnr(strasseHnr)
                    giit_stelle.set_plzStadt(plzStadt)

                    if giit_stelle.stellenBeschreibung != "":
                        if "stuttgart" in giit_stelle.stellenBeschreibung.lower():
                            if giit_stelle.emailAdresse != None:
                                if giit_stelle.arbeitgeberName != None:
                                    if giit_stelle.strasseHnr != None:
                                        if giit_stelle.plzStadt != None:
                                            if giit_stelle.emailAdresse not in liste_Firmen and giit_stelle.arbeitgeberName not in liste_Firmen: # Überprüft ob Firma oder E-Mail bereits angeschrieben wurde.
                                                block = False
                                                for word in blacklist_Words:
                                                    if word in giit_stelle.stellenBeschreibung.lower():
                                                        block = True
                                                        print("## BLOCK Wort ##", word)

                                                for firma in blacklist_Firmen:
                                                    if firma in giit_stelle.arbeitgeberName.lower() or firma in giit_stelle.stellenBeschreibung.lower(): # Prüfung ob Firma unerwünscht ist.
                                                        block = True
                                                        print("## BLOCK Firma ##", firma)

                                                if block != True:
                                                    # Konstruieren der Anschrift
                                                    bewerbungAnschrift = giit_stelle.arbeitgeberName + "\n" + giit_stelle.strasseHnr + "\n\n" + giit_stelle.plzStadt

                                                    print()
                                                    print("Bewerbungsanschrift:")
                                                    print()
                                                    print(bewerbungAnschrift)
                                                    print()

                                                    # Konstruieren der E-Mail
                                                    if TESTMODUS == True:
                                                        emailAdresse = TESTEMAIL # Email zu Testzwecken

                                                    else:
                                                        emailAdresse = giit_stelle.emailAdresse
                                                    
                                                    emailBetreff = mailData.emailBetreff
                                                    gesamtAnsprache = "Sehr geehrte Damen und Herren,"
                                                    emailGesamtText = gesamtAnsprache + "\n\n" + mailData.emailText.replace("\t", "")

                                                    # Konstuieren des Bewerbungs-PDFs / Anhangs
                                                    pdfM.create_anschreiben_overlay(bewerbungAnschrift, datum_anschreiben, gesamtAnsprache, overlay_anschreiben_pdf)
                                                    pdfM.merge_pdfs(anschreiben_pdf, overlay_anschreiben_pdf, output_anschreiben_pdf)
                                                    print(f"Anschreiben PDF wurde erstellt: {output_anschreiben_pdf}")

                                                    pdfM.create_lebenslauf_overlay(datum_lebenslauf, overlay_lebenslauf_pdf)
                                                    pdfM.merge_pdfs(lebenslauf_pdf, overlay_lebenslauf_pdf, output_lebenslauf_pdf)
                                                    print(f"Lebenslauf PDF wurde erstellt: {output_lebenslauf_pdf}")

                                                    # Overlay-Dateien löschen, da sie nicht mehr benötigt werden
                                                    time.sleep(1.5)
                                                    if os.path.exists(overlay_anschreiben_pdf):
                                                        os.remove(overlay_anschreiben_pdf)
                                                        print(f"Overlay-Datei '{overlay_anschreiben_pdf}' wurde gelöscht")

                                                    if os.path.exists(overlay_lebenslauf_pdf):
                                                        os.remove(overlay_lebenslauf_pdf)
                                                        print(f"Overlay-Datei '{overlay_lebenslauf_pdf}' wurde gelöscht")

                                                    # Erstelle die finale PDF-Datei für die Bewerbung
                                                    pdfs = ["pdf_work\\output_anschreiben.pdf", "pdf_work\\output_lebenslauf.pdf", "pdf_work\\zeugnisse.pdf", "pdf_work\\Infoblatt_Praktikumsbetriebe_GFN.pdf"]
                                                    output_pdf_path = "Bewerbung als Praktikant Fachinformatiker Anwendungsentwicklung von Manuel Kilzer.pdf"
                                                    safe_output_pdf_path = "pdf_safe\\Bewerbung " + giit_stelle.arbeitgeberName + time.strftime(" %d_%m_%Y") + "_giit.pdf"
                                                    pdfM.make_final_pdf(pdfs, output_pdf_path)

                                                    if TESTMODUS != True: # Gesichterte PDFs nur von wirklich verschickten Bewerbungen.
                                                        pdfM.make_final_pdf(pdfs, safe_output_pdf_path)

                                                    print("Die PDFs wurden erfolgreich zusammengefügt.")

                                                    # Output-Dateien löschen, da sie nicht mehr benötigt werden
                                                    time.sleep(1.5)
                                                    if os.path.exists(output_anschreiben_pdf):
                                                        os.remove(output_anschreiben_pdf)
                                                        print(f"Output-Datei '{output_anschreiben_pdf}' wurde gelöscht")

                                                    if os.path.exists(output_lebenslauf_pdf):
                                                        os.remove(output_lebenslauf_pdf)
                                                        print(f"Output-Datei '{output_lebenslauf_pdf}' wurde gelöscht")

                                                    emailAnhang = "Bewerbung als Praktikant Fachinformatiker Anwendungsentwicklung von Manuel Kilzer.pdf"
                                                    
                                                    # Versende E-Mail und füge Firma der Liste (liste_Firmen) hinzu um doppelte E-Mails zu vermeiden.
                                                    smtpM.send_email(smtpEmail, smtpPw, emailAdresse, emailBetreff, emailGesamtText, emailAnhang)

                                                    # Füge aktuelle Firma der Firmenliste hinzu bei denen sich schon beworben wurde.
                                                    liste_Firmen.extend([giit_stelle.arbeitgeberName, giit_stelle.emailAdresse])
                                                    time.sleep(1.5)

                                                    # Lösche die bereits gesendete PDF-Datei
                                                    if os.path.exists(output_pdf_path):
                                                        os.remove(output_pdf_path)
                                                        print(f"Bewerbung '{output_pdf_path}' wurde gelöscht.")

                                                    time.sleep(1.5)

                                                    if TESTMODUS == True:
                                                        break

                                        else:
                                            print("1")

                                    else:
                                        print("Straße None")

                                else:
                                    print("3")

                            else:
                                print("Email None")

                        else:
                            print("Stuttgart None")

                    else:
                        print("6")

                    time.sleep(5)

    except Exception as error:
        print("Hauptprogramm Fehler!", error)

    finally:
        # Schliessen des Browsers
        if driver:
            driver.quit()

        # Der Firmenspeicher muss nur aktualisiert werden wenn scharf verschickt wird.
        if TESTMODUS == False:
            # Schreibe eine aktualisierte firmenspeicher.csv.
            print("Aktualisiere Firmen-CSV Datei.")
            with open(CSV_DATEIPFAD, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                for firma in liste_Firmen:
                    writer.writerow([firma])

        os.system("color F") # Konsolenschriftfarbe wird auf Weiß gesetzt.
        exit()