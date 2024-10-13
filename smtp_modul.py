"""
Dateiname: smtp_modul.py
Autor: Manuel Kilzer
Datum: 08. Oktober 2024

Beschreibung:
    Dieses Modul stellt die Funktionen für das versenden von Emails zur verfügung.

Copyright (c) 2024 Manuel Kilzer
"""

# Standardbibliotheken
import smtplib

# E-Mail-Verarbeitung
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Email-Versand mit Anhang
def send_email(smtpEmail, smtpPw, empfaenger, betreff, email_Text, pdf_Filename):
    print("### Sende Mail ###")
    print("Epfänger-Email:", empfaenger)
    print("Betreff:", betreff)
    print("Nachricht:")
    print(email_Text)

    try:
        # E-Mail-Konfiguration
        sender_email = smtpEmail
        sender_passwort = smtpPw
        receiver_email = empfaenger
        subject = betreff
        body = email_Text

        # E-Mail erstellen
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # PDF-Datei als Anhang hinzufügen
        attachment = open(pdf_Filename, "rb")

        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {pdf_Filename}")

        message.attach(part)

        # Verbindung zum SMTP-Server herstellen
        with smtplib.SMTP_SSL("web311.dogado.net", 465) as server:
            server.login(sender_email, sender_passwort)

            # E-Mail senden
            server.sendmail(sender_email, receiver_email, message.as_string())

        print("E-Mail erfolgreich versendet!")
        return True

    except Exception as error:
        print("send_email()", error)
        return False