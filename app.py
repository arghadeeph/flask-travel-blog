from flask import Flask, render_template, request, redirect, flash, url_for
from models import db, Users, Posts, Contacts
from flask_migrate import Migrate
from slugify import slugify
from flask_mail import Mail, Message
from config import Config
from auth import AuthManager

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)  

mail = Mail(app)  
    
auth = AuthManager(db, Users)

# Middleware for session timeout
@app.before_request
def handle_auth():
    auth.check_session_timeout(app.permanent_session_lifetime.total_seconds())

@app.context_processor
def inject_user():
    return dict(current_user=auth.get_current_user())

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/category')
@auth.login_required
def category():
    return render_template('category.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if name and email and subject:

            # Send email
            msg = Message(
            subject=subject+ ' from '+ name,
            reply_to=email,
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_DEFAULT_SENDER']],
            body=message
            )
            mail.send(msg)

            newContact = Contacts(name=name, email=email, subject=subject, message=message )
            db.session.add(newContact)
            db.session.commit()
            flash('Thank you for contacting us!', 'success')

        flash('Please enter valid data!', 'danger')
        return redirect('/contact')    
        
    return render_template('contact.html')

@app.route('/blog')
def blog():
    return render_template('blog-details.html')


@app.route('/dashboard', methods=['GET'])
@auth.login_required
def dashboard():
    return 'Welcome to Dashboard'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        if auth.authenticate(name, password):
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Invalid credentials!', 'warning')
        return redirect('/login')

    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    auth.logout()
    return redirect('/')


@app.route('/my-posts', methods=['GET'])
def myaccount():
    return render_template('my-posts.html')
    

if __name__ == '__main__':
    app.run(debug=True)