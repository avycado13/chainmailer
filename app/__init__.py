from flask import Flask, render_template, request, redirect, url_for
import random, string
import googlemaps
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


def generate_random_string(length):
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


app = Flask(__name__)
app.config.from_pyfile("config.py")
gmaps = googlemaps.Client(key=app.config["GMAPS_KEY"])
app.config["SECRET_KEY"] = generate_random_string(16)  # Required for Flask-WTForms

db = SQLAlchemy(app)


# Define the database model
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    coords = db.Column(db.String(200), nullable=False)


# Flask-WTForms form
class EntryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    location = StringField(
        "Location", validators=[DataRequired()], render_kw={"id": "autocomplete"}
    )
    submit = SubmitField("Submit")


# Flask-Admin setup
admin = Admin(app, template_mode="bootstrap3")
admin.add_view(ModelView(Entry, db.session))


@app.route("/", methods=["GET", "POST"])
def index():
    form = EntryForm()
    if request.method == "POST" and form.validate_on_submit():
        name = form.name.data
        location = form.location.data
        # Save the entry to the database
        new_entry = Entry(name=name, location=location,coords=gmaps.geocode(location))
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("index.html", form=form,api_key=app.config["GMAPS_KEY"])


# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
