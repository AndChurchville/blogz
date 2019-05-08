from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:lc101@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, body, title):
        self.body = body
        self.title = title
    
        
@app.route('/blog', methods =['POST', 'GET'])
def index():
    entry = Blog.query.all()
    posted_blog = Blog.query.all()
    return render_template('blog.html', entry=entry, posted_blog=posted_blog)


@app.route('/newpost', methods=['POST','GET'])
def newpost():
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
            new_entry = Blog(entry_log, title_log)
            db.session.add(new_entry)
            db.session.commit()
            newpost = new_entry.id
            print('OFHOSFHSOIHNODVSNOFNVSOIFN')
            print(newpost)
            display = "/displaypost?id=" + str(newpost)
           
        return redirect(display)
            
    return render_template('newpost.html')

@app.route('/displaypost')
def displaypost():
    
    blogpost = request.args.get("id","newpost")
    posted_blog = Blog.query.get(blogpost)
    return render_template('displaypost.html', posted_blog=posted_blog)


if __name__ == '__main__':
    app.run()      
