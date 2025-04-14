from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests
import gzip

app = Flask(__name__)

# Load movie data and similarity matrix
movies_dict = pickle.load(open('movies2.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

with gzip.open('similarity.pkl.gz', 'rb') as f:
    similarity = pickle.load(f)

def fetch_poster(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=878530df31874f3219751073790dab44&language=en-US'
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

@app.route('/', methods=['GET', 'POST'])
def index():
    movie_titles = movies['title'].values
    recommendations = []

    if request.method == 'POST':
        selected_movie = request.form['movie']
        names, posters = recommend(selected_movie)
        recommendations = zip(names, posters)

    return render_template('index.html', movie_titles=movie_titles, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
