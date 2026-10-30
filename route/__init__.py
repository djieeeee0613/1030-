import re

PHONE_RE = re.compile(r"^\+?\d{8,13}$")


def normalize_phone(s):
    """電話只留數字（可有開頭 +），方便比對"""
    return re.sub(r"[\s\-()]", "", s or "")


def register_routes(app):
    from route.events import bp as events_bp
    from route.registrations import bp as registrations_bp

    app.register_blueprint(events_bp)
    app.register_blueprint(registrations_bp)
