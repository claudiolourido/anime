import random
from flask import Flask, request, session, render_template, redirect, url_for
import requests
import logging

app = Flask(__name__)
app.secret_key = 'secret'

open('log.log', 'w').close()
logging.basicConfig(filename="log.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def rand_date() -> tuple[int, int, int]:
    year = random.randint(2010, 2025)
    month = random.randint(1, 12)
    day = random.randint(1, 30)
    if month < 10:
        month = '0' + str(month)
    if day < 10:
        day = '0' + str(day)
    return year, month, day

def rand_sort() -> str:
    list_sort = ["mal_id", "title", "start_date", "end_date", 
                 "score", "scored_by", "popularity", "members", "favorites"]
    sort_by = random.choice(list_sort)
    if sort_by in ['popularity', 'members', 'favorites', 'score']:
        return sort_by + '&sort=desc'
    else:
        return sort_by + f'&sort={random.choice(["asc", "desc"])}'

def rand_anime() -> list[dict]:
    while True:
        year, month, day = rand_date()
        chosen_sort = rand_sort()
        url = f'https://api.jikan.moe/v4/anime?start_date={year}-{month}-{day}&order_by={chosen_sort}'
        res = requests.get(url)
        data = res.json().get('data', [])
        logger.info("Api Call \n Anime list:")
        for x in data:
            logger.info(x['title'])
        return data

def valid_anime(data: list[dict]) -> dict:
    valid_animes = []
    logger.info("VALID ANIMES:")
    for anime in data:
        if anime['members'] > 5000:
            valid_animes.append(anime)
            logger.info(anime['title'])
    return random.choice(valid_animes) if valid_animes else None

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/reset')
def reset_score():
    session['score'] = 0
    session['n_guesses'] = 0
    return redirect(url_for('home'))

@app.route('/randomanime', methods=['GET', 'POST'])
def random_anime():
    if request.method == 'GET':
        if 'score' not in session:
            session['score'] = 0
            session['n_guesses'] = 0
        if session['n_guesses'] == 10:
            return render_template("end.html", score=session['score'])
        while True:
            animes = rand_anime()
            anime = valid_anime(animes)
            if anime:
                break
        return render_template("image_guess.html", title=anime['title'], image_url=anime['images']['jpg']['image_url'])
    else:
        guess = request.form.get('guess', '').lower()
        correct_title = request.form.get('correct_title', '').strip().lower()
        image_url = request.form.get('image_url')
        guess_words = guess.split()
        title_words = correct_title.split()
        correct = any(word in title_words for word in guess_words)
        if correct:
            session['score'] += 1
            result = "✅ Correct!"
        else:
            result = f"❌ Wrong! The correct answer was: {correct_title.title()}"
        session['n_guesses'] += 1
        return render_template("image_result.html", result=result, image_url=image_url, score=session['score'])

@app.route('/describeanime', methods=['GET', 'POST'])
def describe_anime():
    if request.method == 'GET':
        if 'score' not in session:
            session['score'] = 0
            session['n_guesses'] = 0
        if session['n_guesses'] == 10:
            return render_template("end.html", score=session['score'])
        while True:
            animes = rand_anime()
            anime = valid_anime(animes)
            if anime:
                break
        return render_template("desc_guess.html", title=anime['title'], synopsis=anime.get('synopsis', 'No description available.'))
    else:
        guess = request.form.get('guess', '').lower()
        correct_title = request.form.get('correct_title', '').strip().lower()
        synopsis = request.form.get('synopsis')
        guess_words = guess.split()
        title_words = correct_title.split()
        correct = any(word in title_words for word in guess_words)
        if correct:
            session['score'] += 1
            result = "✅ Correct!"
        else:
            result = f"❌ Wrong! The correct answer was: {correct_title.title()}"
        session['n_guesses'] += 1
        return render_template("desc_result.html", result=result, synopsis=synopsis, score=session['score'])

if __name__ == '__main__':
    print("Server is starting at http://127.0.0.1:5000")
    app.run(debug=True)
