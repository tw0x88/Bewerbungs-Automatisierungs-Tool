"""
Dateiname: pdf_modul.py
Autor: Manuel Kilzer
Datum: 08. Oktober 2024

Beschreibung:
    Dieses Modul stellt die Funktionen für die PDF- Erstellung, Manipulation und Verschmelzung zur verfügung. 

Copyright (c) 2024 Manuel Kilzer
"""

# Drittanbieter-Bibliotheken
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PyPDF2 import PdfWriter, PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import PyPDF2

# Funktion erstellt das Textoverlay für das Anschreiben
def create_anschreiben_overlay(adresse, datum, anrede, overlay_filename):
    print("Erstelle PDF Textoverlay für das Anschreiben.")
    pdf = canvas.Canvas(overlay_filename, pagesize=A4)
    width, height = A4

    pdfmetrics.registerFont(TTFont("calibri", "C:\\Windows\\Fonts\\calibri.ttf"))
    pdfmetrics.registerFont(TTFont("calibri-bold", "C:\\Windows\\Fonts\\calibrib.ttf"))

    adresse_x = 57 # X-Position des Textes
    adresse_y = height - 162  # Y-Position des Textes

    zeile = 0
    for line in adresse.split('\n'):
        if zeile == 0:
            pdf.setFont("calibri-bold", 12)

        else:
            pdf.setFont("calibri", 12)

        pdf.drawString(adresse_x, adresse_y, line)
        adresse_y -= 14.4  # Zeilenabstand
        zeile += 1

    pdf.drawString(413.7, 636.4, datum)
    pdf.setFont("calibri", 11)
    pdf.drawString(56.5, 504.8, anrede)
    
    pdf.showPage()
    pdf.save()

# Funktion erstellt das Textoverlay für den Lebenslauf
def create_lebenslauf_overlay(datum, overlay_filename):
    print("Erstelle PDF Textoverlay für den Lebenslauf.")
    pdf = canvas.Canvas(overlay_filename, pagesize=A4)
    width, height = A4

    pdfmetrics.registerFont(TTFont("calibri", "C:\\Windows\\Fonts\\calibri.ttf"))
    pdf.setFont("calibri", 10)
    pdf.drawString(185.7, 83.5, datum)
    pdf.showPage()
    pdf.save()

# Funktion, um das Overlay mit der bestehenden PDF zu verschmelzen
def merge_pdfs(base_pdf, overlay_pdf, output_pdf):
    base = PdfReader(base_pdf)
    overlay = PdfReader(overlay_pdf)
    writer = PdfWriter()

    # Beide PDFs zusammenführen (Overlay über Basis-PDF)
    for page_num in range(len(base.pages)):
        base_page = base.pages[page_num]
        overlay_page = overlay.pages[0]  # Da das Overlay nur eine Seite hat

        # Die Seiten zusammenfügen (Overlay auf die Basis-PDF)
        base_page.merge_page(overlay_page)
        writer.add_page(base_page)

    # Zusammengeführte PDF speichern
    with open(output_pdf, "wb") as out_file:
        writer.write(out_file)

def make_final_pdf(pdf_list, output_path):
    # Erstellt einen PDF-Merger
    pdf_merger = PyPDF2.PdfMerger()
    
    # Alle PDFs der Liste hinzufügen
    for pdf in pdf_list:
        pdf_merger.append(pdf)

    # Zusammengeführtes PDF speichern
    with open(output_path, 'wb') as output_pdf:
        pdf_merger.write(output_pdf)

    pdf_merger.close() # Nötig damit der Merger die Dateien vollständig loslässt.