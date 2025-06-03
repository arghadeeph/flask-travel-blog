from flask import Flask, render_template, request, redirect, flash, url_for
from models import db, Users, Posts, Contacts
from flask_migrate import Migrate
from slugify import slugify
from flask_mail import Mail, Message
from config import Config
from auth import AuthManager
from utils import upload_image
from math import ceil
from bs4 import BeautifulSoup


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

    posts = Posts.query.order_by(Posts.created_at.desc()).all()
    for post in posts:
        post.clean_content = strip_html(post.content)

    return render_template('index.html', posts=posts)


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

@app.route('/blog/<string:slug>')
def blog(slug):
    return render_template('blog-details.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        if auth.authenticate(name, password):
            return redirect(request.args.get('next') or url_for('myposts'))
        flash('Invalid credentials!', 'warning')
        return redirect('/login')

    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    auth.logout()
    return redirect('/')


@app.route('/my-posts', methods=['GET'])
@auth.login_required
def myposts():

    page = request.args.get('page', 1, type=int)
    perPage = 4

    current_user_id = auth.get_current_user().id
    countTotal = Posts.query.filter_by(user_id = current_user_id).count()
    offset = ( page - 1 ) * perPage
    limit = perPage
    totalPage = ceil(countTotal/perPage)

    posts = Posts.query.filter_by(user_id = current_user_id)\
                        .order_by(Posts.created_at.desc())\
                        .offset(offset)\
                        .limit(limit)\
                        .all()
    for post in posts:
        post.clean_content = strip_html(post.content)

    return render_template('my-posts.html', posts=posts, page = page, total_pages = totalPage)

@app.route('/add-post', methods=['GET', 'POST'])
@auth.login_required
def addpost():
    if request.method == 'POST':

        title = request.form.get('title')
        slug = generate_unique_slug(title)
        content = request.form.get('content')
        image = request.files.get('image')
        image_filename = upload_image(image, app.config['FILE_UPLOAD_PATH']+'blog/')

        current_user_id = auth.get_current_user().id 
        blog = Posts(user_id = current_user_id, title=title, slug=slug, content=content, image=image_filename)
        db.session.add(blog)
        db.session.commit()
        flash('Blog created successfully!', 'success')
        return redirect('/add-post')

    return render_template('add-post.html')
    
# -------- Reusable Functions ---------    
def generate_unique_slug(title):
    base_slug = slugify(title)
    slug = base_slug
    counter = 2
    while Posts.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug   
 
def strip_html(html):
    return BeautifulSoup(html, "html.parser").get_text()

if __name__ == '__main__':
    app.run(debug=True)