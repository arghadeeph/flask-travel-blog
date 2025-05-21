from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from slugify import slugify
from flask_mail import Mail, Message
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = '87c18504f18e2aa1b2b3698a95221240'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travelblog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration for mail server (example using Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

db = SQLAlchemy(app)
migrate = Migrate(app, db)  

mail = Mail(app)

class Users(db.Model):
    id = db.Column(db.Integer,  primary_key = True)    
    name = db.Column(db.String(100), nullable=False)
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
    

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/category')
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
            sender=os.getenv('MAIL_USERNAME'),
            recipients=[os.getenv('MAIL_DEFAULT_SENDER')],
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


if __name__ == '__main__':
    app.run(debug=True)