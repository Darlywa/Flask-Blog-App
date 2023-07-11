from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NameForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os


app = Flask(__name__)

#Instantiate the editor
ckeditor = CKEditor(app)

#database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#secret key
app.config["SECRET_KEY"] = "my super secret form that nobody suppose to know"


UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

#Initialise the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(int(user_id))



#create the route for the blog post
@app.route("/add_blog_post", methods = ["GET", "POST"])
def add_post():
    #title = None
    form = PostForm()
    
    if form.validate_on_submit():
        #extract posts and store them at the post variable
    
        poster = current_user.id
        post = Posts_blog(title=form.title.data, poster_id=poster, content=form.content.data, slug=form.slug.data)
        #clear the form
        form.title.data = ""
        #form.author.data = ""
        form.content.data = ""
        form.slug.data = ""

        db.session.add(post)
        db.session.commit()

        flash("Blog post added successfully!")
    return render_template("add_post.html", form=form)


#create admin page
#create route 
@app.route("/admin")
@login_required
def admin():

    if current_user.id == 1:
        return render_template("admin.html")
    else:
        flash("Access denied...")
        return redirect(url_for('dashboard'))

#create dashboard page
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.location = request.form['location']
        name_to_update.username = request.form['username']
        name_to_update.profile_pic = request.files['profile_pic']

        #get the profile pic file name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)

        #append something to the file name such that no user will have the same file name by setting uuid
        pic_name = str(uuid.uuid1()) + "_" + pic_filename

        #save the picture
        #saver = request.files['profile_pic']
        #saver.save(os.path.join(app.config["UPLOAD_FOLDER"]), pic_name)
        #name_to_update.profile_pic.save(os.path.join(app.config["UPLOAD_FOLDER"]), pic_name)

        #assign the pic_name for onward committing to database
        name_to_update.profile_pic = pic_name

        try:
            db.session.commit()
            name = name_to_update.name
            flash("User details successfully updated!")
            return render_template("dashboard.html", id = id, form=form, name_to_update = name_to_update )
        except:
            flash("Error!, it seems a problem has occurred... Please try again.")
            return render_template("dashboard.html", id =id, form=form, name_to_update = name_to_update )
    else:
        return render_template("dashboard.html", form=form, id = id, name_to_update = name_to_update )

    return render_template("dashboard.html")

#create logout function
@app.route("/logout", methods= ["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out, thanks for stopping bye!")
    return redirect(url_for('login'))

#create login page
@app.route("/login", methods= ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #check the password
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successfull")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong password, try again..")
        else:
            flash("The username does not exist. Please, sign up.")

    return render_template("login.html", form = form)


#create page that list all our blog post
@app.route("/posts")
def posts():
    posts = Posts_blog.query.order_by(Posts_blog.date_added)
    return render_template("posts.html", posts=posts)

#create individual blog post page
@app.route("/post/<int:id>")
def post(id):
    post = Posts_blog.query.get_or_404(id)
    return render_template("post.html", post=post)


#create the edit post
@app.route("/edit/posts/<int:id>", methods= ["GET", "POST"])
def edit_post(id):
    #get the posts from database
    post = Posts_blog.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        #take the form data and replace the initial content of post
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data

        #update database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for('post', id = post.id))
    if post.poster.id == current_user.id:
        #popluate the form with the previous information in the database   
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template("edit_post.html", form=form)
    else:
        flash("You are not authorised to edit that post")
        posts = Posts_blog.query.order_by(Posts_blog.date_added)
        return render_template("posts.html", posts=posts)


#create delete post function
@app.route("/delete/post/<int:id>")
@login_required
def delete_post(id):
    #Retrieve the post whose id is passed
    post_to_delete = Posts_blog.query.get_or_404(id)
    if current_user.id == post_to_delete.poster.id:

        try:
            #delete the post
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Post has been deleted")
            #Get all the posts and redirect to blog posts page
            posts = Posts_blog.query.order_by(Posts_blog.date_added)
            return render_template("posts.html", posts=posts)
        except:
            #if there is an error message
            flash("Whoops! there is an error, please try again...")
            #Get all the posts and redirect to blog posts page
            posts = Posts_blog.query.order_by(Posts_blog.date_added)
            return render_template("posts.html", posts=posts)
    else:
        flash("You are not authorised to delete that post.")
        #Get all the posts and redirect to blog posts page
        posts = Posts_blog.query.order_by(Posts_blog.date_added)
        return render_template("posts.html", posts=posts)

#create delete route
@app.route("/delete/<int:id>")
@login_required
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User successfully deleted")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", 
                           form = form, 
                           name = name,
                           our_users = our_users
                           )
    except:
        flash("Whoos! something went wrong, please try again...")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", id =id,
                           form = form, 
                           name = name,
                           our_users = our_users
                           )


#create update route for the user form
@app.route("/update/<int:id>", methods = ["GET", "POST"])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.location = request.form['location']
        name_to_update.username = request.form['username']

        name_to_update.profile_pic = request.files['profile_pic']

        #get the profile pic file name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)

        #append something to the file name such that no user will have the same file name by setting uuid
        pic_name = str(uuid.uuid1()) + "_" + pic_filename

        #save the picture
        saver = request.files['profile_pic']
        saver.save(os.path.join(app.config["UPLOAD_FOLDER"], pic_name))

        #name_to_update.profile_pic.save(os.path.join(app.config["UPLOAD_FOLDER"]), pic_name)

        #assign the pic_name for onward committing to database
        name_to_update.profile_pic = pic_name
        try:
            db.session.commit()
            name = name_to_update.name
            flash("User details successfully updated!")
            return render_template("dashboard.html", id = id, form=form, name_to_update = name_to_update )
        except:
            flash("Error!, it seems a problem has occurred... Please try again.")
            return render_template("update.html", id =id, form=form, name_to_update = name_to_update )
    else:
        return render_template("update.html", form=form, id = id, name_to_update = name_to_update )


#create the user form route
@app.route("/user/add", methods = ['GET', 'POST'])
def add_user():
    try:
        name = None
        form = UserForm()
        if form.validate_on_submit():
            #check if any user has the same email - query the database
            user = Users.query.filter_by(email=form.email.data).first()
            if user is None:
                hashedPassword = generate_password_hash(form.password_hash.data, "sha256")
                user = Users(name=form.name.data, username=form.username.data, email = form.email.data, location = form.location.data, password_hash=hashedPassword)
                db.session.add(user)
                db.session.commit()
                name = form.name.data
                flash("User added successfully!")
            else: 
                flash("User already has an existing email address.")
            form.name.data = ""
            form.username.data = ""
            form.email.data = ""
            form.location.data = ""
            form.password_hash.data = ""
        our_users = Users.query.order_by(Users.date_added) 
        return render_template("add_user.html", 
                               form = form, 
                               name = name,
                               our_users = our_users
                               )
    except:
        flash("User creation failed, please try again")
        our_users = Users.query.order_by(Users.date_added) 
        return render_template("add_user.html", 
                               form = form, 
                               name = name,
                               our_users = our_users)


#create route 
@app.route("/")
def index():
    username = "<strong>Darlington</strong>"

    favoritePizza = ["pepperoni", "cheese", "vegan", 50]
    return render_template("index.html", username=username, favoritePizza=favoritePizza)


@app.route("/user/<name>")
def user_page(name):
    return render_template("user.html", name=name)

#create error custom page
#custom error page for pages that do not exist
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#Internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

#create the name form route
@app.route('/name', methods = ['GET', 'POST'])
def name():
    name = None
    form = NameForm()

    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Form submitted successfully")
    return render_template("name.html", name=name, form=form)

#create a test_pw page 
@app.route('/test_pw', methods = ['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        #clear the form
        form.email.data = ""
        form.password.data = ""

        #Search the database using the email and return the first item in the search list
        pw_to_check = Users.query.filter_by(email=email).first()
        #num_users = Users.query.filter_by(email=email).count()

        #compare the hashed password and the password entered by user
        passed = check_password_hash(pw_to_check.password_hash, password)
    
    return render_template("test_pw.html", email=email, password = password, passed = passed, pw_to_check=pw_to_check, form = form)

#create an api that returns json file
@app.route("/json")
def get_json():
    favoritePizza = {
    "Peter": "pepperoni",
    "John": "cheese",
    "Darlington": "Mushroom"
    }
    return favoritePizza

#pass search to the navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


#create a search function
@app.route("/search", methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts_blog.query
    if form.validate_on_submit():
        searched = form.searched.data
        posts = posts.filter(Posts_blog.content.like('%' + searched + '%'))
        posts = posts.order_by(Posts_blog.title).all()
        return render_template('search.html', form=form, posts=posts, searched=searched)



#----database section-----------------------------#


#create blog post database model
class Posts_blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    #author = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    slug =  db.Column(db.String(255), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Foreign key to link users (refers to the primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


#create a user database model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    location = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(250), nullable=True)
    #User can many posts
    posts = db.relationship('Posts_blog', backref='poster')

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute.")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verifyPassword(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<Name %r>" % self.name





