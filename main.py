from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lc101blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, body, title, owner):
        self.body = body
        self.title = title
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

# main page that shows all blogs right now     
@app.route('/blog', methods =['POST', 'GET'])
def blog():
    user = User.query.all()
    entry = Blog.query.all()
    posted_blog = Blog.query.all()
    #users

    user_id = request.args.get("userid", "entry")
    if "userid" in request.args:
        userblog = Blog.query.filter_by(owner_id=user_id).all()
        return render_template ('userdisplay.html', userblog=userblog, entry=entry)

    return render_template('blog.html', entry=entry, posted_blog=posted_blog)

#Created a homepage ('/') that shows all usernames. call it index. 
@app.route('/', methods=['POST', 'GET'])
def index():
    name = User.query.all()
    usernames = User.query.all()
    return render_template('index.html', name=name, usernames=usernames)

#newpost is the page where you create the blog post
@app.route('/newpost', methods=['POST','GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method =='POST':
        entry_log = request.form['entry']
        title_log = request.form['title']
    
        entry_error = ""
        title_error = ""
       

        if entry_log == "":
            entry_error = "Please Add A Body"
            entry_log = ""

        if title_log == "":
            title_error = "Please Enter A Title"
            title_log = ""

        if entry_error or title_error:
            return render_template("newpost.html", entry_log=entry_log, title_log=title_log, entry_error=entry_error,
            title_error=title_error)
        else:
            new_entry = Blog(entry_log, title_log, owner)
            db.session.add(new_entry)
            db.session.commit()
            newpost = new_entry.id
            display = "/displaypost?id=" + str(newpost)
        blogs = Blog.query.filter_by(owner=owner).all()
        return redirect(display)
            
    return render_template('newpost.html')

#display post is the post where the single post is shown
@app.route('/displaypost')
def displaypost():
    
    blogpost = request.args.get("id","newpost")
    posted_blog = Blog.query.get(blogpost)
    return render_template('displaypost.html', posted_blog=posted_blog)



#the login and setups
# TODO-add app.before_request. remeber to add index that shows all usernames
@app.before_request
def require_login():
    allowed_routes = ['login','signup','blog','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            flash('Logged in! Welcome ' + username + '!')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
    return render_template('login.html')
            

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
    # validate data
        username_error = ""
        password_error = ""
        verify_error = ""
        if not username:
            username_error = "Please enter a username"
        elif len(username) < 3 or len(username) > 20:
            username_error = "Not a valid username"
            username = ''
        else:
            hasSpace = True
            for char in username:
                if char.isspace():
                    hasSpace = False
                if not hasSpace:
                    username_error = "Username must not contain any spaces"
                    username = ''
        
        if not password:
            password_error = "Please enter a password"
        elif len(password) < 3 or len(password) > 20:
            password_error = "Not a valid password"
        else:
            hasSpace = True 
            for char in password:
                if char.isspace():
                    hasSpace = False
                if not hasSpace:
                    password_error = "Password must not contain any spaces"
    
        if password != verify:
            verify_error = "Passwords must match"
        if not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            #'remember' the user using session['thing']
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', password_error=password_error, verify_error=verify_error, username_error=username_error, 
            username=username, password=password, verify=verify)
    
    # exsisting user 
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Username already exists. Please try again.', 'error')

    return render_template('signup.html')


@app.route('/logout')
def logout():
    del session['username']
    flash('Logged out! Goodbye!')
    return redirect('/blog')


if __name__ == '__main__':
    app.run()      
