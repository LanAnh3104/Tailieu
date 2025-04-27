import os
import shutil
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
from datetime import datetime

load_dotenv()

EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FOLDER = BASE_DIR
BACKUP_FOLDER = os.path.join(BASE_DIR, 'backup')

if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)

def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Email đã gửi thành công")
    except Exception as e:
        print(f"❌ Lỗi khi gửi email: {e}")

def backup_database():
    try:
        files = os.listdir(SOURCE_FOLDER)
        backup_count = 0
        for file in files:
            if file.endswith('.sql') or file.endswith('.sqlite3'):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_filename = f"{timestamp}_{file}"
                src = os.path.join(SOURCE_FOLDER, file)
                dst = os.path.join(BACKUP_FOLDER, backup_filename)
                shutil.copy2(src, dst)
                backup_count += 1

        if backup_count > 0:
            subject = "Backup thành công ✅"
            body = f"Đã sao lưu {backup_count} file vào {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
            send_email(subject, body)
        else:
            subject = "Backup thất bại ❌"
            body = "Không tìm thấy file để sao lưu."
            send_email(subject, body)

    except Exception as e:
        subject = "Backup thất bại ❌"
        body = f"Lỗi khi sao lưu: {str(e)}"
        send_email(subject, body)

schedule.every(1).minutes.do(backup_database)
#schedule.every().day.at("00:00").do(backup_database)
while True:
    schedule.run_pending()
    time.sleep(1)
