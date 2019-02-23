from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "abcde"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    writer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, writer):
        self.title = title
        self.body = body
        self.writer = writer

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(25))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref = 'writer')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog','index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():

    writers = User.query.all()
    return render_template('index.html', writers=writers)

@app.route('/blog', methods=['GET'])
def blog():

    if len(request.args) == 0:
        blogs = Blog.query.all()
        #EDIT THIS TO JOIN TABLE
        writers = Blog.query.join(User, User.id==Blog.writer_id).filter_by(email=User.email).first()
        return render_template('blog.html',blogs=blogs, writers=writers)
    
    if request.args.get('user'):
        return redirect('/login')
        #CHANGE THIS SO IT SHOWS A LIST OF BLOGS BY THE USER

    else:
        blog_id = Blog.query.filter_by(id=int(request.args.get('id'))).first()
        writer = logged_in_user()
        return render_template('blog.html', blog_title=blog_id.title, blog_body=blog_id.body, writer=writer.email, writer_id=writer.id) 

@app.route('/newpost', methods=['POST','GET'])
def add_post():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_content = request.form['content']

        title_error = ""
        content_error = ""

        if len(blog_title) < 1:
            title_error = "Title must contain at least 1 character"
            return render_template('newpost.html', title_error=title_error, blog_content=blog_content)
        if len(blog_content) < 1:
            content_error = "Content must contain at least 1 character"
            return render_template('newpost.html', content_error=content_error, blog_title=blog_title)
#THIS DOESN'T WORK PROPERLY
        else:
            new_post = Blog(blog_title, blog_content, logged_in_user())
            db.session.add(new_post)
            db.session.commit()
            return redirect ('/blog?id=' + str(new_post.id))

    return render_template('newpost.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        user_error = ""

        if len(email) < 3:
            user_error = "User name must be greater than two characters."
            email = ""

        for char in email:
            if char == " ":
                user_error = "User name cannot contain spaces."
                email = ""

        password = request.form['password']
        password_error = ""

        if len(password) < 3:
            password_error = "Password must be greater than two characters."
            password = ""

        for char in password:
            if char == " ":
                password_error = "Password cannot contain spaces."
                password = ""

        verify = request.form['verify']
        verify_error = ""
        if verify != password:
            verify_error = "Password does not match."
            verify = ""

        if user_error or password_error or verify_error:
            return render_template('signup.html', email=email, user_error=user_error, password_error=password_error, verify_error=verify_error)            
        else:
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/newpost')
            else:
                flash("User already exist. Please select a different username to register.", 'error')
                return redirect('/signup')

    return render_template('signup.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("User does not exist. Please register for an account.", 'error')
            return redirect('/login')
        if user and user.password != password:
            flash('Incorrect password.', 'error')
            return redirect('/login')
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")  
            return redirect('/newpost')

    return render_template('login.html')

def logged_in_user():
    writer = User.query.filter_by(email=session['email']).first()
    return writer

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()