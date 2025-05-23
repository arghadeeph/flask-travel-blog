from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from slugify import slugify
from flask_mail import Mail, Message
from config import Config
from auth import AuthManager

app = Flask(__name__)

app.config.from_object(Config)


db = SQLAlchemy(app)
migrate = Migrate(app, db)  

mail = Mail(app)

class Users(db.Model):
    id = db.Column(db.Integer,  primary_key = True)    
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100))
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationship: one user has many posts
    posts = db.relationship('Posts', backref='user', lazy=True)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

class Contacts(db.Model):
    id = db.Column(db.Integer,  primary_key = True)    
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())    
    
auth = AuthManager(db, Users)

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
def dashboard():
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    return 'You are in the login page!'

    

if __name__ == '__main__':
    app.run(debug=True)