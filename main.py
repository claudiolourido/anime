import random
from flask import Flask, request, session, render_template_string, redirect, url_for
import requests

app = Flask(__name__)


app.secret_key = 'secret'  


def rand_anime():
    while True:
        year = random.randint(2010, 2025)
        month = random.randint(1, 12)
        day = random.randint(1, 30)  

        list_sort = [
            "mal_id", "title", "start_date", "end_date", 
            "score", "scored_by", "popularity", "members", "favorites"
        ]
        sort_by = random.choice(list_sort)

        if sort_by in ['popularity', 'members', 'favorites', 'score']:
            chosen_sort = sort_by + '&sort=desc'
        else:
            orders = ['asc', 'desc']
            chosen_sort = sort_by + f'&sort={random.choice(orders)}'

        if month < 10:
            month = '0' + str(month)
        if day < 10:
            day = '0' + str(day)

        url = f'https://api.jikan.moe/v4/anime?start_date={year}-{month}-{day}&order_by={chosen_sort}'
        res = requests.get(url)
        valid_animes = []
        data = res.json().get('data', [])
        
        for anime in data:
            if anime['members'] > 5000:
                valid_animes.append(anime)
            
        if len(valid_animes) > 0:
            return random.choice(valid_animes)
        



@app.route('/')
def home():
    return render_template_string('''
        <html>
            <head><title>Anime Game Menu</title></head>
            <body>
                <center>
                    <h1>Welcome to the Anime Guessing Game!</h1>
                    <form action="/randomanime">
                        <button type="submit">🎴 Guess by Image</button>
                    </form>
                    <br>
                    <form action="/describeanime">
                        <button type="submit">📜 Guess by Description</button>
                    </form>
                </center>
            </body>
        </html>
    ''')


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
            return render_template_string('''
                <html>
                    <head><title> End of game</title><head>
                    <body>
                        <center>
                            <h2>Total Score {{score}} / 10 </h2>
                            <a href="/reset">🏠 Main Menu</a>
                        </center>
                    </body>
                                          
                </html>
    '''
            , score = session['score'])
        
        anime = rand_anime()

        return render_template_string('''
            <html>
                <head><title>Guess by Image</title></head>
                <body>
                    <center>
                        <h2>Guess the Anime Title from the Image</h2>
                        <img src="{{ image_url }}" alt="Anime Image" width="200"><br><br>
                        <form method="post">
                            <input type="hidden" name="correct_title" value="{{ title }}">
                            <input type="hidden" name="image_url" value="{{ image_url }}">
                            <input name="guess" placeholder="Your guess here">
                            <button type="submit">Submit</button>
                        </form>
                    </center>
                </body>
            </html>
        ''', title=anime['title'], image_url=anime['images']['jpg']['image_url'])

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

        return render_template_string('''
            <html>
                <head><title>Result</title></head>
                <body>
                    <center>
                        <h2>{{ result }}</h2>
                        <img src="{{ image_url }}" width="200"><br><br>
                        <a href="/randomanime">Try Another</a><br>
                        <a href="/reset">🏠 Main Menu</a>
                        <p> Score: {{ score }} / 10</p>
                    </center>
                </body>
            </html>
        ''', result=result, image_url=image_url, score=session['score'])




@app.route('/describeanime', methods=['GET', 'POST'])
def describe_anime():
    if request.method == 'GET':
        if 'score' not in session:
            session['score'] = 0
            session['n_guesses'] = 0


        if session['n_guesses'] == 10:
            return render_template_string('''
                <html>
                    <head><title> End of game</title><head>
                    <body>
                        <center>
                            <h2>Total Score {{score}} / 10 </h2>
                            <a href="/reset">🏠 Main Menu</a>
                        </center>
                    </body>
                                          
                </html>
    '''
            , score = session['score'])
        
        anime = rand_anime()
        return render_template_string('''
            <html>
                <head><title>Guess by Description</title></head>
                <body>
                    <center>
                        <h2>Guess the Anime from the Description</h2>
                        <p style="max-width: 500px;">{{ synopsis }}</p>
                        <form method="post">
                            <input type="hidden" name="correct_title" value="{{ title }}">
                            <input type="hidden" name="synopsis" value="{{ synopsis }}">
                            <input name="guess" placeholder="Your guess here">
                            <button type="submit">Submit</button>
                        </form>
                    </center>
                </body>
            </html>
        ''', title=anime['title'], synopsis=anime.get('synopsis', 'No description available.'))

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


        return render_template_string('''
            <html>
                <head><title>Result</title></head>
                <body>
                    <center>
                        <h2>{{ result }}</h2>
                        <p style="max-width: 500px;">{{ synopsis }}</p>
                        <a href="/describeanime">Try Another</a><br>
                        <a href="/reset">🏠 Main Menu</a>
                        <p> Score: {{ score }} / 10</p>

                    </center>
                </body>
            </html>
        ''', result=result, synopsis=synopsis, score=session['score'])

if __name__ == '__main__':
    app.run(debug=True)
