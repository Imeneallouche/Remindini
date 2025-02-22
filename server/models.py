from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    ForeignKey,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


# --- Modèle Utilisateur ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(
        String, unique=True, nullable=False
    )  # Email de l'utilisateur (connexion et notifications)
    phone_number = Column(
        String, nullable=False
    )  # Numéro de téléphone pour recevoir les SMS
    google_email = Column(
        String, unique=True, nullable=True
    )  # Email Google pour la connexion OAuth
    google_token = Column(
        String, nullable=True
    )  # Jeton OAuth pour accéder à l'API Google Calendar
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    calendar_events = relationship(
        "CalendarEvent", back_populates="user", cascade="all, delete-orphan"
    )
    sms_notifications = relationship(
        "SMSNotification", back_populates="user", cascade="all, delete-orphan"
    )
    temperature_readings = relationship(
        "TemperatureReading", back_populates="user", cascade="all, delete-orphan"
    )


# --- Modèle pour les événements Google Calendar ---
class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # Propriétaire de l'événement
    event_id = Column(
        String, unique=True, nullable=False
    )  # ID fourni par Google Calendar
    summary = Column(String, nullable=False)  # Titre ou résumé de l'événement
    description = Column(Text)  # Description optionnelle
    start_time = Column(DateTime, nullable=False)  # Début de l'événement
    end_time = Column(DateTime, nullable=False)  # Fin de l'événement
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="calendar_events")
    notifications = relationship(
        "SMSNotification", back_populates="event", cascade="all, delete-orphan"
    )


# --- Modèle pour les notifications SMS ---
class SMSNotification(Base):
    __tablename__ = "sms_notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # Utilisateur destinataire de la notification
    calendar_event_id = Column(
        Integer, ForeignKey("calendar_events.id"), nullable=True
    )  # Optionnellement lié à un événement
    phone_number = Column(
        String, nullable=False
    )  # Numéro de téléphone auquel le SMS a été envoyé (historique)
    message = Column(String, nullable=False)  # Contenu du SMS
    status = Column(String, default="pending")  # Statut : pending, sent, failed, etc.
    sent_at = Column(DateTime)  # Date d'envoi, si applicable
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="sms_notifications")
    event = relationship("CalendarEvent", back_populates="notifications")


# --- Modèle pour les relevés de température ---
class TemperatureReading(Base):
    __tablename__ = "temperature_readings"
    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # L'utilisateur associé au dispositif de mesure
    temperature = Column(Float, nullable=False)  # Valeur mesurée par le capteur
    reading_time = Column(DateTime, default=datetime.utcnow)  # Horodatage de la lecture

    # Relation
    user = relationship("User", back_populates="temperature_readings")


# --- Modèle pour la configuration globale de la passerelle ---
class GatewayConfig(Base):
    __tablename__ = "gateway_config"
    id = Column(Integer, primary_key=True)

    # Configuration pour le module GSM/SMS
    gsm_module = Column(String)  # Ex : SIM800L
    sms_api_key = Column(String)  # Clé API ou identifiant pour RaspiSMS

    # Configuration pour l'intégration Google Calendar
    google_calendar_id = Column(String)  # Identifiant du calendrier à surveiller
    google_api_key = Column(String)  # Clé API pour accéder à Google Calendar

    # Configuration pour le capteur de température et seuils d'alerte
    temperature_threshold = Column(Float)  # Seuil de déclenchement des alertes
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Fonctions d'initialisation de la BDD ---
def init_db(db_url="sqlite:///iot_project.db"):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


# --- Exemple d'utilisation ---
if __name__ == "__main__":
    engine = init_db()
    session = get_session(engine)

    # Création d'une configuration globale par défaut si non existante
    if session.query(GatewayConfig).count() == 0:
        config = GatewayConfig(
            gsm_module="SIM800L",
            sms_api_key="votre_sms_api_key",
            google_calendar_id="votre_calendar_id",
            google_api_key="votre_google_api_key",
            temperature_threshold=25.0,
        )
        session.add(config)
        session.commit()
