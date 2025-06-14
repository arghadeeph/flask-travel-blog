from functools import wraps
from flask import redirect, request, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

class AuthManager:
    def __init__(self, db, user_model, login_url='login'):
        self.db = db
        self.user = user_model
        self.login_url = login_url

    def login_user(self, user):
        session.permanent = True
        session['user_id'] = user.id
        session['last_active'] = datetime.now().timestamp()    

    def authenticate(self, username, password):
        user = self.user.query.filter_by(email=username).first()
        # Checking if valid user
        if user and check_password_hash(user.password, password):
            self.login_user(user)
            return True
        return False
    
    def is_authenticated(self):
        return 'user_id' in session
    
    def get_current_user(self):
        if 'user_id' in session:
            return self.user.query.get(session['user_id'])
        return None
    
    def login_required(self, func):       
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.is_authenticated():
                next_url = request.referrer or url_for('index')
                return redirect(url_for(self.login_url, next=next_url))
            return func(*args, **kwargs)
        return wrapper
    
    def logout(self):
        session.clear()

    def check_session_timeout(self, timeout_seconds):
        
        if self.is_authenticated():
            now = datetime.now().timestamp()
            last_active = session.get('last_active', now)
            if now - last_active > timeout_seconds:
                self.logout()
            else:
                session['last_active'] = now
        
    def hash_password(self, password):
        return generate_password_hash(password)