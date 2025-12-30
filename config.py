import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
    
    # Notifications
    NOTIFICATION_RECIPIENTS = os.getenv('NOTIFICATION_RECIPIENTS', '').split(',')
    
    # Upload folders
    QR_CODES_FOLDER = os.path.join('static', 'qr_codes')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
