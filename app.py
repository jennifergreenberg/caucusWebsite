###########################################################################################################################################
#                                                                                                                                         #
#                                                           App Setup                                                                     #
#                                                                                                                                         #
###########################################################################################################################################

from flask import Flask, render_template, url_for, g, redirect, request, flash, session, Blueprint
#import toastr as toastr
app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

# jinja2 setup
import jinja2 as ninja
import os
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja2_env = ninja.Environment(loader=ninja.FileSystemLoader(template_dir))

# SQLite database setup
app.config.from_mapping(
    SECRET_KEY="dev",
    DATABASE=os.path.join(app.instance_path, "myData.sqlite"),
)
from db import init_app, get_db, insert, remove, init_app
from dataVisualBuilder import createGraph
init_app(app) # initilize the database

# App setup
init_app(app)


###########################################################################################################################################
#                                                                                                                                         #
#                                                           Login Features                                                                #
#                                                                                                                                         #
###########################################################################################################################################

import login
from login import login_required
app.register_blueprint(login.bp)




###########################################################################################################################################
#                                                                                                                                         #
#                                                           Routing                                                                       #
#                                                                                                                                         #
###########################################################################################################################################

# Home Page
@app.route('/')
def home():
    
    return render_template('home.html')


# Settings Page
@app.route('/settings', methods=("GET", "POST"))
@login_required
def settings():
    # Add Candidate Form
    if request.method == "POST":
        if "insert" in request.form:
            name = request.form["candName"]
            bio = request.form["candBio"]
            image = request.form["filename"]
            error = None

            if not name or not bio or not image:
                error = "Missing Information"

            if error is not None:
                flash(error)
            else:
                insert("candidate", ["name", "bio", "img"], [name, bio, image])
                return render_template('index.html', alert="insert")

        # Remove a Candidate Form
        elif "delete" in request.form:
            candName = request.form["candName"]
            remove("candidate", "name", candName)
            return render_template('index.html', alert="delete")

        # Seetings Form
        elif "settings" in request.form:
            db = get_db()
            realign = request.form["realign"]
            numPeople = request.form["people"]
            error = None

            if not numPeople:
                error = "Missing Information"

            if error is not None:
                flash(error)
            else:
                insert("settings", ["realign", "numPeople"], [realign, numPeople])
                return render_template('index.html', alert="settings")

    # Main Page
    return render_template('index.html')

# Count Page
@app.route('/count', methods=("GET", "POST"))
def count():
    if request.method == "POST":
        db = get_db()
        numOfVotes = request.form['numVotes']
        name = request.form['Candname']
        db.execute(
                "UPDATE candidate WHERE name=(?) SET numVotes=(?)", (name, numOfVotes),
            )
    return render_template('votes.html')


# Data Page
@app.route('/data')
@login_required
def data():
    for filename in os.listdir('static/images'):
        if filename.startswith('graph'):
            os.remove('static/images/' + filename)
    filename = createGraph()
    return render_template('data.html', graphPath=filename)


local = True
if __name__ == '__main__':
    if local:
        import os
        HOST = os.environ.get('SERVER_HOST', 'localhost')
        try:
            PORT = int(os.environ.get('SERVER_PORT', '5555'))
        except ValueError:
            PORT = 5555
        app.run(HOST, PORT)
    else:
        app.run(debug=True)