import datetime
import os

import bleach
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

## Delete this code:
# import requests
# posts =

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


## strips invalid tags/attributes
def strip_invalid_html(content):
    allowed_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'br', 'div', 'dl', 'dt',
                    'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
                    'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'strike',
                    'span', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
                    'thead', 'tr', 'tt', 'u', 'ul']

    allowed_attrs = {
        'a': ['href', 'target', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
    }

    cleaned = bleach.clean(content,
                           tags=allowed_tags,
                           attributes=allowed_attrs,
                           strip=True)

    return cleaned


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


db.create_all()


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


# <!--{{url_for('edit_post', post_id=post.id)}}-->

# noinspection PyPackageRequirements
# show post route, routing with id
@app.route("/post/<int:post_id>")
def show_post(post_id):
    # get all blog post then pass to our blog page
    requested_post = BlogPost.query.get(post_id)

    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# new post route
@app.route('/new-post', methods=["GET", "POST"])
def create_post():
    # initializing our form
    form = CreatePostForm()
    if request.method == "POST":
        # getting date blog post was created
        date = datetime.date.today().strftime("%B %d, %Y")

        if form.validate_on_submit():
            blog_title = form.title.data
            blog_subtitle = form.subtitle.data
            blog_author = form.author.data
            blog_img_url = form.img_url.data
            blog_body = strip_invalid_html(request.form.get('body'))
            print(blog_title, blog_subtitle, blog_author, blog_img_url, blog_body)

            # creating mew data to add to our database
            new_post = BlogPost(title=blog_title,
                                subtitle=blog_subtitle,
                                date=date,
                                body=blog_body,
                                author=blog_author,
                                img_url=blog_img_url
                                )
            # adding data to the database
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form=form)


# edit existing post route
@app.route('/edit-post/<int:post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    blog_post = BlogPost.query.get(post_id)

    # creating form and passing existing data to it
    form = CreatePostForm(title=blog_post.title,
                          subtitle=blog_post.subtitle,
                          author=blog_post.author,
                          img_url=blog_post.img_url,
                          body=blog_post.body,
                          )

    # updating blog post in our database
    if form.validate_on_submit():
        blog_post.title = form.title.data
        blog_post.subtitle = form.subtitle.data
        blog_post.author = form.author.data
        blog_post.img_url = form.img_url.data
        blog_post.body = strip_invalid_html(request.form.get('body'))

        db.session.commit()
        # redirect to post page
        return redirect(url_for('show_post', post_id=post_id))
    return render_template('make-post.html', id=post_id, form=form)


@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    blog_post = BlogPost.query.get(post_id)
    # print(blog_post)
    db.session.delete(blog_post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run()
