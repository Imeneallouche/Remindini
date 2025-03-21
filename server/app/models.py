from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True) 

    sms_service_activated = db.Column(db.Boolean, default=True, nullable=True)
    temperature_service_activate= db.Column(db.Boolean, default=False, nullable=True)
    humidity_service_activate= db.Column(db.Boolean, default=False, nullable=True)
    temperature_treshold = db.Column(db.Float, nullable=False, default=30.0)   
    humidity_treshold = db.Column(db.Float, nullable=False, default=90.0) 
    reminder_delay = db.Column(db.Integer, nullable=False, default=60)  #Always stored in minutes
    reminder_unit = db.Column(db.String(10), default="minutes")

    token_id = db.Column(db.Integer, db.ForeignKey('token.id'), unique=True)

    # Relation One-to-One avec Token
    token = db.relationship("Token", back_populates="user")

    # Relation One-to-Many avec EventNotification
    notified_events = db.relationship("EventNotification", back_populates="user", cascade="all, delete-orphan")

    def add_notified_event(self, event_id):
        """Ajoute un événement notifié."""
        if not EventNotification.query.filter_by(event_id=event_id, user_id=self.id).first():
            event = EventNotification(event_id=event_id, user_id=self.id)
            db.session.add(event)
            db.session.commit()

    def get_notified_events(self):
        """Retourne la liste des identifiants d'événements notifiés."""
        return [event.event_id for event in self.notified_events]

    def remove_notified_event(self, event_id):
        """Supprime un événement notifié."""
        event = EventNotification.query.filter_by(event_id=event_id, user_id=self.id).first()
        if event:
            db.session.delete(event)
            db.session.commit()

    def is_event_notified(self, event_id):
     """Vérifie si un événement a déjà été notifié (retourne un booléen)."""
     return EventNotification.query.filter_by(event_id=event_id, user_id=self.id).first() is not None
    
    def count_notified_events(self):
     return len(self.notified_events)
    


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256), unique=True, nullable=False)
    refresh_token = db.Column(db.String(256), unique=True, nullable=False)
    token_uri = db.Column(db.String(256), nullable=False)  
    client_id = db.Column(db.String(256), nullable=False)
    client_secret = db.Column(db.String(256), nullable=False)
    scopes = db.Column(db.String(256), nullable=False)
    expiry = db.Column(db.String(256), nullable=False)

    # Relation One-to-One avec User
    user = db.relationship("User", back_populates="token", uselist=False)



class EventNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.String(255), nullable=False, unique=True)  # ID de l'événement Google
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relation avec User
    user = db.relationship("User", back_populates="notified_events")

