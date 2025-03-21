
import json
import time
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from .user_service import   UserService
import dateutil.parser 
import locale 

def get_calendar_service(user):
    """Récupère le service Google Calendar avec les credentials du user."""
    try:
        if not user.token:
            print("L'utilisateur n'a pas de token associé.")
            return None
        
        credentials = Credentials(
            token=user.token.token,
            refresh_token=user.token.refresh_token,
            token_uri=user.token.token_uri,
            client_id=user.token.client_id,
            client_secret=user.token.client_secret,
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
            #scopes=user.token.scopes.split()  # Convertir la chaîne en liste si nécessaire
        )
        return build("calendar", "v3", credentials=credentials)

    except Exception as e:
        print(f"Erreur lors de l'initialisation du service Google Calendar: {e}")
        return None


def check_events(user):
    """Vérifie les événements en fonction du délai de rappel défini par l'utilisateur et envoie un SMS si nécessaire."""
    service = get_calendar_service(user)
    if service is None:
        return

    now = datetime.now(timezone.utc)

    # Récupérer le délai défini par l'utilisateur (par défaut à 60 min si non défini)
    reminder_delay = user.reminder_delay if user.reminder_delay is not None else 60

    time_min = now.isoformat()
    time_max = (now + timedelta(minutes=reminder_delay + 3)).isoformat()  # Intervalle dynamique

    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        print(f"🔍 Vérification des événements pour {user.username} (Délai de rappel: {reminder_delay} min) ...")
        print(f"Intervalle recherché : {now.strftime('%Y-%m-%d %H:%M:%S')} → {(now + timedelta(minutes=reminder_delay + 3)).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Événements récupérés : {len(events)}")

        if not events:
            print(f"Aucun événement imminent pour {user.username}.")
        else:
            for event in events:
                event_id = event['id']  # ID unique de l'événement Google Calendar
                
                # Vérifier si l'utilisateur a déjà été notifié pour cet événement
                if user.is_event_notified(event_id):
                    print(f"L'utilisateur {user.username} a déjà été notifié pour l'événement {event_id}.")
                    continue
                
                start_str = event['start'].get('dateTime', event['start'].get('date'))
                start_dt = dateutil.parser.isoparse(start_str)
                
                # Vérifier si l'événement est dans l'intervalle [reminder_delay, reminder_delay + 3] minutes
                delta_minutes = (start_dt - now).total_seconds() / 60
                if reminder_delay <= delta_minutes <= (reminder_delay + 3):
                    print(f"📅 Événement trouvé : {event.get('summary', 'Sans titre')} - {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"⏳ Temps restant avant l'événement : {delta_minutes:.2f} min (Délai requis : {reminder_delay}-{reminder_delay + 3})")

                    # Définir la langue locale en français sous Linux
                    try:
                        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
                    except locale.Error:
                        print("⚠ Impossible de définir la locale en français. Les dates seront en anglais.")

                    # Convertir la date en heure locale
                    start_dt_local = start_dt.astimezone()

                    # Formater la date en français
                    formatted_date = start_dt_local.strftime("%A %d %B %Y à %Hh%M")

                    # Construire le message amélioré
                    message = f"🔔 Rappel : \"{event.get('summary', 'Événement sans titre')}\" est prévu le {formatted_date}."
                    send_sms(user, message, event_id)
                    print(f"📤 Envoi du SMS pour {user.username} - {message}")


    except Exception as e:
        print(f"Erreur lors de la récupération des événements: {e}")

def send_sms(user, message, event_id):
    """Envoie un SMS avec Gammu et met à jour la base de données RaspiSMS."""
    import mysql.connector
    from datetime import datetime
    import uuid

    # Gammu SMS sending command
    command = ["gammu", "--config", "/etc/gammu-smsdrc", "sendsms", "TEXT", user.phone_number, "-text", message]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"SMS envoyé à {user.phone_number} : {message}")
            
            # Establish connection to RaspiSMS database
            conn = mysql.connector.connect(
                host='localhost',  # Adjust if different
                user='raspisms',
                password='GjN0ZCgUIOF8POUzud1eRuFoov1QYTtE',
                database='raspisms'
            )
            cursor = conn.cursor()
            
            # Prepare data for insertion
            now = datetime.now()
            unique_uid = str(uuid.uuid4())[:12]  # Generate a unique identifier
            
            # SQL query to insert into sended table
            insert_query = """
            INSERT INTO sended 
            (at, text, destination, flash, status, uid, adapter, id_user, id_phone, mms, originating_scheduled, created_at) 
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Prepare values
            values = (
                now,  # at
                message,  # text
                user.phone_number,  # destination
                0,  # flash (0 for normal SMS)
                'unknown',  # status
                unique_uid,  # uid
                'adapters\\GammuAdapter',  # adapter
                1,  # id_user (assuming default user ID is 1)
                1,  # id_phone (assuming default phone ID is 1)
                0,  # mms (0 for SMS)
                None,  # originating_scheduled
                now  # created_at
            )
            
            # Execute the insert
            cursor.execute(insert_query, values)
            conn.commit()
            
            # Close database connection
            cursor.close()
            conn.close()
            
            # Add the event to notified events
            user.add_notified_event(event_id)
            
            return True
        else:
            print(f"Erreur d'envoi du SMS à {user.phone_number}: {result.stderr}")
            return False
    
    except mysql.connector.Error as db_err:
        print(f"Erreur de base de données : {db_err}")
        return False
    except Exception as e:
        print(f"Exception lors de l'envoi du SMS: {e}")
        return False


#juste un print pour la vérification: 
#def send_sms(phone_number, message):
#    print(f" un message = {message} envoyé à: {phone_number}")

# def reminder():
#     from app import create_app  
#     app = create_app()
#     """Vérifie les rappels pour tous les utilisateurs toutes les 5 minutes."""
#     user_service = UserService()
#     while True:
#         with app.app_context():
#             users = user_service.get_all_users()
#             for user in users:
#                 if user.sms_service_activated: 
#                     print(user.username)
#                     check_events(user)
#                     print("Attente avant la prochaine vérification...")
#                     time.sleep(10)  


import time
import threading
from flask import current_app
from app.services.user_service import UserService
import dateutil.parser
import locale
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 🔒 Verrou pour éviter plusieurs exécutions simultanées de `reminder()`
reminder_execution_lock = threading.Lock()

def reminder():
    """Thread qui vérifie les rappels toutes les 5 minutes."""
    from app import create_app  
    app = create_app()

    with app.app_context():
        user_service = UserService()

        while True:
            with reminder_execution_lock:  # 🔒 Empêche plusieurs exécutions en parallèle
                users = user_service.get_all_users()
                for user in users:
                    if user.sms_service_activated:
                        print(user.username)
                        check_events(user)

                print("Attente avant la prochaine vérification...")

            time.sleep(20)  # Pause globale de 5 minutes pour éviter de surcharger le CPU










#def test_reminder():
    # """Teste la récupération des événements pour l'utilisateur 1."""
    # user_service = UserService()
    # while True:
    #     with app.app_context():  # Assurer que l'application Flask est active
    #         user = user_service.get_user_by_id(2)  # Accès à la BDD avec SQLAlchemy
    #         if not user:
    #             print("L'utilisateur avec ID 1 n'existe pas.")
    #             return

    #         if user.sms_service_activated:
    #             check_events(user)
    #             print("Attente d'une minute avant la prochaine vérification...")
    #             time.sleep(10)  # Pause de 1 minute

# if __name__ == "__main__":
#     reminder()  # Exécuter uniquement la fonction de test

