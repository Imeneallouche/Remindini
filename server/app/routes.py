from flask import Blueprint, jsonify, request, session
from .services.user_service import UserService
from .schemas import UserSchema, TokenSchema, EventNotificationSchema
from .services.sensor_service import get_latest_sensor_data
from flask_cors import CORS



api_bp = Blueprint('api', __name__)
CORS(api_bp, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all API endpoints

user_service = UserService()
user_schema = UserSchema()
users_schema = UserSchema(many=True)



@api_bp.route('/user/create', methods=['POST'])
def create_user():
    """Crée un nouvel utilisateur et associe un token Google."""
    data = request.get_json()

    required_fields = ['username', 'email', 'phone_number', 'token']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    username = data['username']
    email = data['email']
    phone_number = data['phone_number']
    token_data = data['token']  # Maintenant, le token est un dictionnaire

    existing_user = user_service.get_user_by_email1(email)
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 409

    new_user = user_service.create_user(username, email, phone_number, token_data)
    return jsonify(user_schema.dump(new_user)), 201


@api_bp.route('/users', methods=['GET'])
def get_users():
    """Récupère la liste des utilisateurs."""
    users = user_service.get_all_users()
    return jsonify(users_schema.dump(users))


@api_bp.route('/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    """Récupère les informations d’un utilisateur spécifique."""
    user = user_service.get_user_by_id(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user_schema.dump(user))



@api_bp.route('/update_user/<int:id>', methods=['PUT'])
def update_user(id):
    user = user_service.get_user_by_id(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()

    reminder_delay = None
    if "reminder_value" in data and "reminder_unit" in data:
        value = int(data["reminder_value"])
        unit = data["reminder_unit"]
        reminder_delay = value * 60 if unit == "hours" else value


    updated_user = user_service.update_user(
        id,
        phone_number=data.get('phone_number'),
        sms_service_activated=data.get('sms_service_activated'),
        reminder_delay=reminder_delay,
        reminder_unit=data.get('reminder_unit'),
        temperature_service_activate=data.get('temperature_service_activate'),
        humidity_service_activate=data.get('humidity_service_activate'),
        temperature_treshold=data.get('temperature_treshold'),
        humidity_treshold=data.get('humidity_treshold')
    )

    if not updated_user:
        return jsonify({'message': 'Update failed'}), 400 

    return jsonify(user_schema.dump(updated_user)), 200




@api_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    response, status_code = UserService.delete_user(user_id)
    return jsonify(response), status_code



@api_bp.route("/user/<int:user_id>/notified_event_count", methods=["GET"])
def get_user_notified_event_count(user_id):
        count = user_service.get_user_notified_event_count(user_id)
        if count is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"user_id": user_id, "event_count": count})

# @api_bp.route("/sensor_data", methods=["GET"])
# def fetch_sensor_data():
#     """API route to fetch the latest sensor values."""
#     return get_latest_sensor_data()

"""------------------------------------Ikram part------------------------------"""
"""-----------------------------------------------------------------------------"""

@api_bp.route('/save_user', methods=['POST'])
def save_user():
    """ Endpoint pour enregistrer ou mettre à jour un utilisateur """
    data = request.json

    response, status_code = user_service.save_user(
        username=data.get("username"),
        email=data.get("email"),
        phone=data.get("phone"),
        google_token=data.get("google_token")
    )
    return jsonify(response), status_code



@api_bp.route('/signin_user', methods=['POST'])
def signin_user_route():
    """ Endpoint pour vérifier l'existence d'un utilisateur """
    data = request.json
    email = data.get("email")

    response, status_code = user_service.signin_user(email)
    return jsonify(response), status_code


@api_bp.route('/get_user/<email>', methods=['GET'])
def get_user(email):
    """ Endpoint pour récupérer un utilisateur par email """
    response, status_code = user_service.get_user_by_email(email)
    return jsonify(response), status_code



@api_bp.route('/current_user', methods=['GET'])
def get_current_user():
    """Get current user info from session"""
    # This assumes you store the email in the session when user logs in
    email = session.get('email')
    if not email:
        return jsonify({"error": "No user logged in"}), 401
    
    response, status_code = user_service.get_user_by_email(email)
    if status_code != 200:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"email": email, "username": response.get("username")}), 200



@api_bp.route('/environmental-data/<email>', methods=['GET'])
def get_environmental_data(email):
    """Récupère les données environnementales pour le tableau de bord."""
    # First, get the user to access their thresholds
    user_response, user_status = user_service.get_user_by_email(email)
    
    if user_status != 200:
        return jsonify({"error": "User not found"}), 404
    
    # Get the latest sensor data
    sensor_response, sensor_status = get_latest_sensor_data()
    
    # If there was an error with sensor data, return it
    if sensor_status != 200:
        return sensor_response, sensor_status
    
    # Extract data from responses
    sensor_data = sensor_response.get_json()
    
    # Extract user thresholds - user_response is already a dict
    formatted_data = {
        "temperature": {
            "current": sensor_data["temperature"],
            "threshold": user_response["temperature_treshold"] if "temperature_treshold" in user_response else 30.0
        },
        "humidity": {
            "current": sensor_data["humidity"],
            "threshold": user_response["humidity_treshold"] if "humidity_treshold" in user_response else 90.0
        }
    }
    
    return jsonify(formatted_data), 200


@api_bp.route('/sms-stats', methods=['GET'])
def get_sms_stats():
    """Récupère les statistiques de SMS pour l'utilisateur."""
    try:
        # Si l'email est fourni comme paramètre
        email = request.args.get('email')
        
        # Si pas d'email fourni, retourner un compteur général ou 0
        if not email:
            # Option 1: Compteur global pour tous les utilisateurs
            # count = EventNotification.query.count()
            # Option 2: Retourner simplement 0
            count = 0
            return jsonify({"successCount": count}), 200
        
        # Si email fourni, chercher l'utilisateur
        user = user_service.get_user_by_email1(email)
        if not user:
            return jsonify({"error": "User not found", "successCount": 0}), 200
        
        # Récupérer le nombre d'événements notifiés
        count = user_service.get_user_notified_event_count(user.id)
        return jsonify({"successCount": count if count is not None else 0}), 200
        
    except Exception as e:
        print(f"Error in get_sms_stats: {str(e)}")
        return jsonify({"error": str(e), "successCount": 0}), 500

