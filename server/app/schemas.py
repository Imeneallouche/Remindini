from app import ma
from marshmallow import pre_dump
from .models import User, Token, EventNotification

class TokenSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Token

    id = ma.auto_field()
    token = ma.auto_field()
    refresh_token = ma.auto_field()
    token_uri = ma.auto_field()
    client_id = ma.auto_field()
    client_secret = ma.auto_field()
    scopes = ma.auto_field()
    user = ma.Nested('UserSchema', exclude=('token',), back_populates='token')

class EventNotificationSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EventNotification

    id = ma.auto_field()
    event_id = ma.auto_field()
    user_id = ma.auto_field()
    user = ma.Nested('UserSchema', exclude=('notified_events',), back_populates='notified_events')

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    phone_number = ma.auto_field()
    sms_service_activated = ma.auto_field()
    token_id = ma.auto_field()
    token = ma.Nested(TokenSchema, exclude=('user',), back_populates='user')
    notified_events = ma.Nested(EventNotificationSchema, many=True, exclude=('user',), back_populates='user')
    temperature_service_activate = ma.auto_field()
    humidity_service_activate = ma.auto_field()
    temperature_treshold = ma.auto_field()
    humidity_treshold = ma.auto_field()
    reminder_delay = ma.auto_field()
    reminder_unit = ma.auto_field()

    @pre_dump
    def convert_reminder_delay(self, user, **kwargs):
        """Convert reminder_delay back to the correct unit before sending it to the frontend."""
        if user.reminder_unit == "hours":
            user.reminder_delay = user.reminder_delay // 60  # Convert back to hours
        return user
