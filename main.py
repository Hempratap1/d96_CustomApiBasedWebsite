import os

import requests
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

url = "https://rawg-video-games-database.p.rapidapi.com/games"
URL = f"{url}?key={os.environ.get('key')}"

headers = {
    "X-RapidAPI-Key": os.environ.get('api_key'),
    "X-RapidAPI-Host": "rawg-video-games-database.p.rapidapi.com"
}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('secret_api')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///games.db"
db = SQLAlchemy()
db.init_app(app)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    genre = db.Column(db.String(250), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    ranking = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


response = requests.get(url=URL, headers=headers)

data = response.json()

games = data['results']

with app.app_context():
    db.create_all()
    for game in games:
        # Check if the game with the same title already exists
        existing_game = Game.query.filter_by(title=game['name']).first()
        if not existing_game:
            entry = Game(
                title=game['name'],
                release_year=game['released'],
                genre=', '.join(genre['name'] for genre in game['genres']),
                rating=game['rating'],
                img_url=game['background_image']
            )
            db.session.add(entry)
            db.session.commit()


@app.route("/")
def home():
    result = db.session.execute(db.select(Game).order_by(Game.rating))
    all_games = result.scalars().all()

    for i in range(len(all_games)):
        all_games[i].ranking = len(all_games) - i
    db.session.commit()
    return render_template("index.html", games=all_games)


if __name__ == '__main__':
    app.run(debug=True)
