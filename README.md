# Bewerbungs-Automatisierungs-Tool

## 1. Projektübersicht
Dieses Python-basierte Tool automatisiert den Bewerbungsprozess, indem es Stellenanzeigen von verschiedenen Webseiten crawlt, nach benutzerdefinierten Kriterien filtert, PDF-Bewerbungen erstellt und diese dann per SMTP an passende Unternehmen verschickt. Ziel des Projekts ist es, meine Programmierfähigkeiten im Bereich der Automatisierung und Web-Scraping zu demonstrieren.

Das Tool ist besonders nützlich für Personen, die Bewerbungen effizienter und automatisiert versenden möchten, ohne sich manuell um jeden Schritt kümmern zu müssen. Es richtet sich an IT-Fachkräfte und Entwickler, die Python-basierte Automatisierungslösungen benötigen.

## 2. Funktionen und Anwendungsfälle
### 2.1 Hauptfunktionen
- **Web-Crawling:** Crawlt Stellenanzeigen von verschiedenen Webseiten.
- **Filter:** Filtert die Stellenangebote nach vordefinierten Kriterien.
- **Bewerbungserstellung:** Erstellt Bewerbungs-PDFs aus vorbereiteten Vorlagen (z.B. Anschreiben, Lebenslauf).
- **Automatisierter Versand:** Versendet die Bewerbungen via SMTP an die in den Stellenangeboten gefundenen Ansprechpartner.
- **Konfigurierbare Vorlagen:** Benutzer können ihre eigenen PDF-Vorlagen (Anschreiben, Lebenslauf, Zeugnisse) hinzufügen, die das Programm automatisch verwendet.

### 2.2 Anwendungsfälle
Das Tool ist nützlich für Entwickler, die sich auf ihre Fähigkeiten konzentrieren und den Bewerbungsprozess automatisieren wollen. Es ist besonders geeignet, wenn man einige Bewerbungen verschicken möchte, ohne jede einzelne manuell anzupassen.

## 3. Installation
### 3.1 Voraussetzungen
Um das Tool auszuführen, sind folgende Programme und Module erforderlich:
- **Python 3.xx**
- **Selenium** (zum Web-Crawling)
- **Geckodriver.exe** (für Firefox)
- **Firefox Browser**

### 3.2 Installationsanweisungen
1. Stelle sicher, dass die Geckodriver.exe im selben Pfad enthalten ist und Firefox installiert ist.

2. Lege deine PDF-Bewerbungsvorlagen im pdf_work Ordner ab. Die benötigten Dateien sind:
   - `anschreiben.pdf`
   - `lebenslauf.pdf`
   - `zeugnisse.pdf`
   - `infoblatt.pdf`

3. Passe die Konfiguration in der Datei `config.ini` an.

## 4. Verwendung
### 4.1 Ausführen des Programms
Starte das Programm über die Kommandozeile:
python main.py
