
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_username = os.getenv("SSIS_USER")
smtp_password = os.getenv("SSIS_PASSWORD")


def confim_application(recipient, recipient_name):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
    smtp_connection.starttls()

    smtp_connection.login(smtp_username, smtp_password)

    email_subject = 'Thank you for applying.'
    email_body = f"Hello {recipient_name},\n\nThank you for applying to Gutz. We have received your application and will review it as soon as possible. If you have any questions or need further assistance, please don't hesitate to contact us.\n\nBest regards,\nThe Gutz Team"

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = recipient
    msg['Subject'] = email_subject

    msg.attach(MIMEText(email_body, 'plain'))

    smtp_connection.sendmail(smtp_username, recipient, msg.as_string())

    smtp_connection.quit()
