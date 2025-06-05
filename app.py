from flask import Flask, render_template, request, redirect, flash, url_for
from models import db, Users, Posts, Contacts, PostLikes
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
    page = request.args.get('page', 1, type=int)
    perPagePost = 4

    totalPosts = Posts.query.count()
    totalPages = ceil(totalPosts/perPagePost)

    limit = perPagePost
    offset = (page - 1 ) * perPagePost

    posts = Posts.query.order_by(Posts.created_at.desc()).limit(limit).offset(offset).all()
    for post in posts:
        post.clean_content = strip_html(post.content)

    return render_template('index.html', posts=posts, page=page, totalPages=totalPages)


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
    post = Posts.query.filter_by(slug = slug).first()

    if(post):
        return render_template('blog-details.html', post=post)
    else:
        return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    nextPage = request.args.get('next')

    if request.method == 'POST':
        name = request.form.get('name').strip()
        phone = request.form.get('phone').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('conf_password', '')

        if not name or not phone or not email or not password or not confirm_password:
            flash('All fields are required!', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Password and confirm password do not match!', 'danger')
            return render_template('register.html')
        
        if Users.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return render_template('register.html')
        
        hasPasswprd = auth.hash_password(password)

        newUser = Users(name=name, email=email, phone=phone, password=hasPasswprd)
        db.session.add(newUser)
        db.session.commit()

        auth.login_user(newUser)
        flash('Registration successful!', 'success')
        next_page = request.form.get('next')
        return redirect(next_page or url_for('myposts'))
    
    
    return render_template('register.html', next = nextPage)

@app.route('/login', methods=['GET', 'POST'])
def login():
    nextPage = request.args.get('next')
    if request.method == 'POST':

        for key, value in request.form.items():
            print(f"{key}: {value}")
        
        name = request.form.get('username')
        password = request.form.get('password')
        if auth.authenticate(name, password):
            next_page = request.form.get('next')
            return redirect(next_page or url_for('myposts'))
        flash('Invalid credentials!', 'warning')
        return redirect('/login')

    return render_template('login.html', next = nextPage)


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

@app.route('/like-post/<int:post_id>', methods=['GET', 'POST'])
@auth.login_required
def like_post(post_id):
    if request.method == "POST":
        user_id = auth.get_current_user().id

        new_like = PostLikes(user_id=user_id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()

        return redirect(request.referrer)

    
    
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