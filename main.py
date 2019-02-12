from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    writer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, writer):
        self.title = title
        self.body = body
        self.writer = writer

# Add a user class to handle users - Done

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref = 'writer')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/', methods=['GET'])
def index():
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def blog():

    if len(request.args) == 0:
        blogs = Blog.query.all()
        return render_template('blog.html',blogs=blogs)
    else:
        blog_id = Blog.query.filter_by(id=int(request.args.get('id'))).first()
        return render_template('blog.html', blog_title=blog_id.title, blog_body=blog_id.body)

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

        else:
            new_post = Blog(blog_title, blog_content) #add new parameter for blogs (relationship)
            db.session.add(new_post)
            db.session.commit()
            return redirect ('/blog?id=' + str(new_post.id))

    return render_template('newpost.html')

# @app.route('/signup')

# @app.route('/login')

# @app.route('/index')

# We'll have a logout function that handles a POST
# request to /logout and redirects the user to
# /blog after deleting the username from the session.

if __name__ == '__main__':
    app.run()