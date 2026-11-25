import os
from flask import Flask
app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY'), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.environ.get('RENDER') == 'true')
if not app.secret_key:
    raise RuntimeError('Set SECRET_KEY environment variable')
