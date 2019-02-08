from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['GET'])
def index():
    blogs = Blog.query.all()
    return render_template('blog.html',blogs=blogs)

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
            new_post = Blog(blog_title, blog_content)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/')

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()