from app import db
from ..models import User, Token, EventNotification

class UserService:
    def get_all_users(self):
        return User.query.all()

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)
    
    def get_user_by_email1(self, email):
        return User.query.filter_by(email=email).first()

    def create_user(self, username, email, phone_number, token_data):
        """Crée un utilisateur et associe un token Google."""
        # Création du token
        token = Token(
            token=token_data['token'],
            refresh_token=token_data['refresh_token'],
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=" ".join(token_data['scopes'])
        )

        user = User(
            username=username,
            email=email,
            phone_number=phone_number,
            token=token  # Associe directement le token
        )

        db.session.add(user)
        db.session.commit()
        return user
    


    def save_user(self, username, email, phone, google_token):
        if not email or not phone:
            return {"error": "Missing email or phone"}, 400
        
        existing_user = self.get_user_by_email1(email)  
        if existing_user:
            return {"error": "Existing user with the same email"}, 409
        else:
            # Create a new user with default values for all attributes
            new_user = User(
                username=username,
                email=email,
                phone_number=phone,
                sms_service_activated=True,  
                temperature_service_activate=False,  
                humidity_service_activate=False,  
                temperature_treshold=30.0,
                humidity_treshold=90.0,  
                reminder_delay=60,
                reminder_unit="minutes",
                token=Token(
                    token=google_token["token"],
                    refresh_token=google_token["refresh_token"],
                    token_uri=google_token["token_uri"],
                    client_id=google_token["client_id"],
                    client_secret=google_token["client_secret"],
                    scopes=",".join(google_token["scopes"]),
                    expiry=google_token["expiry"],
                ),
            )

            db.session.add(new_user)
            db.session.commit()
            return {
                    "message": "User saved!",
                    "id": new_user.id, 
                    "username": new_user.username,
                    "email": new_user.email,
                    "phone_number": new_user.phone_number,
                    "sms_service_activated": new_user.sms_service_activated,
                    "temperature_service_activate": new_user.temperature_service_activate,
                    "humidity_service_activate": new_user.humidity_service_activate,
                    "temperature_treshold": new_user.temperature_treshold,
                    "humidity_treshold": new_user.humidity_treshold,
                    "reminder_delay": new_user.reminder_delay
                    }, 200


    def update_user(self, user_id, phone_number=None, sms_service_activated=None, reminder_delay=None, reminder_unit=None, temperature_service_activate=None, humidity_service_activate=None, temperature_treshold=None, humidity_treshold=None):
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        if phone_number:
            user.phone_number = phone_number
        if sms_service_activated is not None:
            user.sms_service_activated = sms_service_activated
        if reminder_delay is not None:
            user.reminder_delay = reminder_delay
        if reminder_unit is not None:
            user.reminder_unit = reminder_unit
        if temperature_service_activate is not None:
            user.temperature_service_activate = temperature_service_activate
        if humidity_service_activate is not None:
            user.humidity_service_activate = humidity_service_activate
        if temperature_treshold is not None:
            user.temperature_treshold = temperature_treshold
        if humidity_treshold is not None:
            user.humidity_treshold = humidity_treshold

        db.session.commit()
        return user


    
    def get_user_notified_event_count(self, user_id):
        """Récupère le nombre d'événements notifiés pour un utilisateur."""
        user = db.session.get(User, user_id)
        if not user:
            return None  # L'utilisateur n'existe pas
        return user.count_notified_events()

    def get_user_by_email(self, email):
        """ Récupère un utilisateur par son email """
        session_db = db.session  # Utilisation de la session SQLAlchemy
        user = session_db.query(User).filter_by(email=email).first()

        if user:
            return {
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "sms_service_activated": user.sms_service_activated,
            "temperature_service_activate": user.temperature_service_activate,
            "humidity_service_activate": user.humidity_service_activate,
            "temperature_treshold": user.temperature_treshold,
            "humidity_treshold": user.humidity_treshold,
            "reminder_delay": user.reminder_delay
            }, 200
        return {"error": "User not found"}, 404


    def signin_user(self, email):
        """ Vérifie si l'utilisateur existe en base de données """
        if not email:
            return {"error": "Missing email"}, 400

        user = db.session.query(User).filter_by(email=email).first()

        if user:
            return {
                "message": "Login successful",
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "sms_service_activated": user.sms_service_activated,
                "temperature_service_activate": user.temperature_service_activate,
                "humidity_service_activate": user.humidity_service_activate,
                "temperature_treshold": user.temperature_treshold,
                "humidity_treshold": user.humidity_treshold,
                "reminder_delay": user.reminder_delay,
                "reminder_unit": user.reminder_unit
            }, 200

        return {"error": "User not found"}, 403

    
    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return {"error": "Utilisateur non trouvé"}, 404
        
        if user.token:
            db.session.delete(user.token) 
        db.session.delete(user)
        db.session.commit()
        return {"message": "Utilisateur supprimé avec succès"}, 200