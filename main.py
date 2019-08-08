from flask import Flask, request, redirect, render_template, session, flash
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
project_dir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(project_dir, "Blogz.db"))
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 't0p5ecr3tk3y'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def all_blogs():
    return Blog.query.all()

def all_users():
    return User.query.all()

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    input_errors = {'username':[], 'password':[]}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        new_user = User(username, password)
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exitsts.', 'username_error')
            return render_template('signup.html')
        if password != password2:
            flash('Passwords must match', 'matching_error')
            return render_template('signup.html', username)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect('/newpost')
    return render_template('signup.html', input_errors=input_errors)



@app.route('/login', methods=['POST', 'GET'])
def login():
    login_input_errors = {'username':[], 'password':[]}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Username invalid', 'username-error')
            return render_template('login.html')
        if password != user.password:
            flash('Password incorrect', 'password-error')
            return render_template('login.html', username=username)
        session['username'] = username
        return redirect('/blog')
    return render_template('login.html', login_input_errors=login_input_errors)

    if not user:
        flash("Username does not exist.", "username_error")
        return render_template('/login')
    if login_password != user.password:
        flash("Incorrect password", "password_error")
        return render_template('/login')
    session['username'] = login_username
    return redirect('/newpost')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/index')

@app.route('/blog')
def blog():
    #pass data between pages via URL with request.args.get()
    username = request.args.get('user')
    if username:
        user = User.query.filter_by(username=username).first()
        user_posts = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('blog.html', user_posts=user_posts, username=username)
    blog_id = request.args.get('id')
    if blog_id != None:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog.html', post=post)
    list_all_blogs = all_blogs()
    list_all_users = all_users()
    return render_template('blog.html', list_all_blogs=list_all_blogs, list_all_users=list_all_users)

@app.route('/post')
def post():
    post_id = request.args.get('id')
    print("here" + post_id)
    current_blog = Blog.query.filter_by().all()
    print(current_blog)
    print("__/n")
    print(type(current_blog))
    print("__/n")
    print(type(current_blog[0].title))
    print("__/n")

    blog_title = current_blog[int(post_id)-1].title
    blog_body = current_blog[int(post_id)-1].body

    return render_template('post.html', blog_title=blog_title, blog_body=blog_body)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    input_errors = {'blog_title':[], 'blog_body':[]}

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        blog_owner = User.query.filter_by(username=session['username']).first()
        no_post = False
        if blog_title == "":
            input_errors['blog_title'].append('Title cannot be blank.')
            no_post = True
        if blog_body == "":
            input_errors['blog_body'].append('Blog post cannot be blank.')
            no_post = True
        if no_post == False:
            new_post = Blog(blog_title, blog_body, blog_owner)
            db.session.add(new_post)
            db.session.commit()
            return render_template('post.html', blog_title=blog_title, blog_body=blog_body)

    return render_template('newpost.html', input_errors=input_errors)

@app.route('/', methods=['POST', 'GET'])
def index():
    list_all_users = all_users()
    return render_template('index.html', list_all_users=list_all_users)

if __name__ == '__main__':
    app.run()