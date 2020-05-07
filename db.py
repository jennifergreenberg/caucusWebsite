import sqlite3

import click
from flask import current_app
from flask import g
from flask.cli import with_appcontext
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def insert(tableName, arguments, values):
    # These arugments should be a list of strings
    # Basically this function runs this command with but with the custom values
    #       db.execute("INSERT INTO candidate (name, bio, img) VALUES (?, ?, ?)", (name, bio, image),)

    db = get_db()
    dbCommand = "INSERT INTO " + tableName + " "
    # fancy population of string
    dbCommand += ("(" + ', '.join(['%s']*len(arguments)) + ") ") % tuple(arguments)
    dbCommand += "VALUES" + " (" + ", ".join("?"*len(arguments)) + ")"
    db.execute(dbCommand, values, )
    db.commit()

def remove(tableName, columnName, item):
    db = get_db()
    dbCommand = "DELETE FROM " + tableName + " WHERE " + columnName +"=(?)"
    db.execute(dbCommand, (item,))
    db.commit()
    
    
labels = [arguments]
men_means = [values]


x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, men_means, width, label='Men')
rects2 = ax.bar(x + width/2, women_means, width, label='Women')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Scores')
ax.set_title('Scores by group and gender')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()


def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


autolabel(rects1)
autolabel(rects2)

fig.tight_layout()

plt.show()
