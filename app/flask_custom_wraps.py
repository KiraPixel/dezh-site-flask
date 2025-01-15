from functools import wraps
from flask import session, redirect, url_for


def validate_sessions():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session or 'password' not in session:
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator