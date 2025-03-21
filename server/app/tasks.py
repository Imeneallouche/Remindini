 from threading import Thread
 from app.services.sms_service import reminder

 def start_reminder_service():
     """Lance le service de rappels en arrière-plan."""
     reminder_thread = Thread(target=reminder, daemon=True)
     reminder_thread.start()
