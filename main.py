import datetime
from dearapi import dearapi
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders
from datetime import datetime
from datetime import timedelta
import time

#skus to check
def load_skus():
    skus = []
    with open('dummy.csv') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            skus.append(row[0])
    return skus

def send_email(to_address, password):
    SUBJECT = 'Test Inventory Report'
    FILENAME = 'report.csv'
    FILEPATH = './report.csv'
    MY_EMAIL = 'jesse@vossdot.com'
    MY_PASSWORD = password
    TO_EMAIL = to_address
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587

    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = COMMASPACE.join([TO_EMAIL])
    msg['Subject'] = SUBJECT

    text = """\
        Hello, please see the attached CSV file for an update on Voss Helmets inventory relevant to your store


        Regards,
        Voss Team
    """
    text_part = MIMEText(text, "plain")
    msg.attach(text_part)

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(FILEPATH, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=FILENAME) 
    msg.attach(part)

    smtpObj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(MY_EMAIL, MY_PASSWORD)
    smtpObj.sendmail(MY_EMAIL, TO_EMAIL, msg.as_string())
    smtpObj.quit()


def execute():
    with open('password.txt') as passfile:
        password = passfile.readline()

    skus = load_skus()


    report = []

    for sku in skus:
        available = api.getAvailability(sku)
        if available > 2:
            report.append([sku, available])

    print(report)

    with open('report.csv', 'w') as csvfile:
        report_writer = csv.writer(csvfile)
        report_writer.writerow(['SKU', 'Quantity'])
        for row in report:
            report_writer.writerow(row)

    send_email('jesse.irwin11@gmail.com', password)



if __name__ == '__main__':
    api = dearapi()
    api.loadCredentials()

    now = datetime.now()

    execute()

    while True:
        #change to days=7 when time is known for weekly updates
        run_at = now + timedelta(minutes=5)
        delay = (run_at - now).total_seconds()
        time.sleep(delay)
        execute()


    

    
    
