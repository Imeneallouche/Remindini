import sys
import os
import time
import datetime
import hashlib
import subprocess
import mysql.connector
import uuid
import json
import dateutil.parser
import locale

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure.storage.blob import BlobServiceClient
from app import db
from app import create_app
from app.services.user_service import UserService
from app.models import EventNotification
from flask_sqlalchemy import SQLAlchemy



# Azure Storage Connection Details
STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=edgestockage2025;AccountKey=3xAx10+RhpFRG9y7zcrR33840kWy6a1rGmNdZydOitEtRYXN5uoX4PfntfDwlxQGz6ONDcH2MjIx+AStT/8QOw==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "container"


def send_sms_with_db_update(phone_number, message,user,device_id):
    """Send SMS with Gammu and update RaspiSMS database."""
    command = ["gammu", "--config", "/etc/gammu-smsdrc", "sendsms", "TEXT", phone_number, "-text", message]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"SMS sent to {phone_number}: {message}")
            
            # Generate unique event ID and log notification
            sensor_event_id = f"sensor_{device_id}_{user.id}_{int(time.time())}"
            if not EventNotification.query.filter_by(event_id=sensor_event_id, user_id=user.id).first():
                 event = EventNotification(event_id=sensor_event_id, user_id=user.id)
                 db.session.add(event)
                 db.session.commit()
                 
                 
            #raspisms
            conn = mysql.connector.connect(
                host='localhost',
                user='raspisms',
                password='GjN0ZCgUIOF8POUzud1eRuFoov1QYTtE',
                database='raspisms'
            )
            cursor = conn.cursor()
            now = datetime.datetime.now()
            unique_uid = str(uuid.uuid4())[:12]
            
            insert_query = """
            INSERT INTO sended 
            (at, text, destination, flash, status, uid, adapter, id_user, id_phone, mms, originating_scheduled, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (now, message, phone_number, 0, 'unknown', unique_uid, 'adapters\\GammuAdapter', 1, 1, 0, None, now)
            cursor.execute(insert_query, values)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        else:
            print(f"SMS sending error to {phone_number}: {result.stderr}")
            return False
    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return False
    except Exception as e:
        print(f"Exception during SMS sending: {e}")
        return False


def read_blob_continuously():
    """Continuously read Blob storage and process sensor data."""
    try:
        app = create_app()
        with app.app_context():
            blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)
            last_blob_hash = None  

            while True:
                now = datetime.datetime.now()
                folder_path = f"{now.year}/{now.month:02d}/{now.day:02d}"
                blob_list = list(container_client.list_blobs(name_starts_with=folder_path + "/"))

                if blob_list:
                    blob_list.sort(key=lambda blob: blob.last_modified, reverse=True)
                    latest_blob = blob_list[0]

                    blob_client = container_client.get_blob_client(latest_blob.name)
                    blob_data = blob_client.download_blob().readall().decode("utf-8")
                    current_blob_hash = hashlib.md5(blob_data.encode("utf-8")).hexdigest()

                    if current_blob_hash != last_blob_hash:
                        print(f"Blob content changed: {latest_blob.name}")
                        try:
                            lines = blob_data.strip().split('\n')
                            for line in lines:
                                try:
                                    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
                                except locale.Error:
                                    print("⚠ Unable to set locale, defaulting to English.")

                                data_json = json.loads(line)
                                temperature = data_json.get("temperature")
                                humidity = data_json.get("humidity")
                                event_time = data_json.get("EventProcessedUtcTime")
                                device_id = data_json.get("IoTHub", {}).get("ConnectionDeviceId")
                                
                                event_dt = dateutil.parser.isoparse(event_time)
                                formatted_date = event_dt.astimezone().strftime("%A %d %B %Y à %Hh%M")
                                
                                user_service = UserService()
                                users = user_service.get_all_users()

                                for user in users:
                                    phone_number = user.phone_number
                                    temp_active = user.temperature_service_activate
                                    humid_active = user.humidity_service_activate
                                    temp_threshold = user.temperature_treshold
                                    humid_threshold = user.humidity_treshold

                                    if temperature and temp_active and temperature > temp_threshold:
                                        message = f"[Alert]: Device {device_id}\n Date: {formatted_date}\n Temperature: {temperature}°C"
                                        print(message)
                                        send_sms_with_db_update(phone_number, message,user,device_id)
                                    
                                    if humidity and humid_active and humidity > humid_threshold:
                                        message = f"[Alert]: Device {device_id}\n Date: {formatted_date}\n Humidity: {humidity}%"
                                        print(message)
                                        send_sms_with_db_update(phone_number, message,user,device_id)
                                    
                                    
                        
                        except json.JSONDecodeError as e:
                            print(f"JSON decoding error: {e}")

                        last_blob_hash = current_blob_hash

                time.sleep(120)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    read_blob_continuously()

