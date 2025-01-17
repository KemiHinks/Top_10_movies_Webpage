from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


response = requests.get(url='https://api.themoviedb.org/3/movie/4133', params={'api_key': 'd0ccd57af64706f1fcb54826eac40096'})
new = response.json()
print(new['original_title'])
print(new["release_date"].split("-")[0])
db = SQLAlchemy()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../movies.db"
# initialize the app with the extension
db.init_app(app)
app.app_context().push()
Bootstrap(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, unique=True, nullable=False)
    description = db.Column(db.String(250), unique=True, nullable=False)
    rating = db.Column(db.Float, unique=True, nullable=False)
    ranking = db.Column(db.Integer, unique=True, nullable=False)
    review = db.Column(db.String, unique=True, nullable=False)
    img_url = db.Column(db.String(250), unique=True, nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Movie {self.title}>'


# once database created comment out
# with app.app_context():
# db.create_all()

# added entry already so commented out code

''' new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)'''


# db.session.add(new_movie)
# db.session.commit()


class MovieUpdate(FlaskForm):
    rating = StringField('rating', validators=[DataRequired()])
    review = StringField('review', validators=[DataRequired()])
    submit = SubmitField("Done")


class AddMovie(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    submit = SubmitField("Done")


@app.route("/")
def home():
    #This line creates a list of all the movies sorted by rating
    all_movies = Movie.query.order_by(Movie.rating).all()

    #This line loops through all the movies
    for i in range(len(all_movies)):
        #This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    form = MovieUpdate()
    # GET VALUE OF ID
    movie_id = request.args.get("id")
    # search sql database by id
    movie_info = Movie.query.get(movie_id)
    if form.validate_on_submit():
        # update rating to new rating
        movie_info.rating = request.form['rating']
        # update description to new description
        movie_info.review = request.form['review']
        db.session.commit()
        return redirect(url_for('select'))
    return render_template("edit.html", updated=form, info=movie_info)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=['GET', 'POST'])
def add():
    add_movie = AddMovie()
    if add_movie.validate_on_submit():
        parameters = {'api_key': 'd0ccd57af64706f1fcb54826eac40096',
                      'query': add_movie.title.data}
        response = requests.get(url='https://api.themoviedb.org/3/search/movie', params=parameters)
        movie_data = response.json()['results'][0]
        return render_template('select.html', data=movie_data)
    return render_template('add.html', new_entry=add_movie)

@app.route("/select")
def select():
    movie_id = request.args.get("id")
    movie_response = requests.get(url=f'https://api.themoviedb.org/3/movie/{movie_id}', params={'api_key': 'd0ccd57af64706f1fcb54826eac40096'})
    added = movie_response.json()
    image = requests.get(url=f'https://api.themoviedb.org/3/movie/{movie_id}/images', params={'api_key': 'd0ccd57af64706f1fcb54826eac40096'})
    latest = Movie(
        title=added['title'],
        year=added["release_date"].split("-")[0],
        description=added["overview"],
        rating=0,
        ranking=0,
        review='None',
        img_url=f'{image}'
    )

    db.session.add(latest)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
