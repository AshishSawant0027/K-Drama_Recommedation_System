from flask import Flask, render_template, request
import requests
import pickle

app = Flask(__name__)

# Load the K-Drama data and similarity matrix
kdrama = pickle.load(open('final_kd.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Function to fetch poster, overview, and additional details from TMDB API
def fetch_poster_and_details(tmdb_id):
    url = f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()

    # Fetch poster
    poster_path = data.get('poster_path')
    full_poster_path = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500"

    # Fetch overview and additional details
    overview = data.get('overview', 'Overview not available')
    first_air_date = data.get('first_air_date', 'N/A')
    last_air_date = data.get('last_air_date', 'N/A')
    name = data.get('name', 'N/A')
    number_of_episodes = data.get('number_of_episodes', 'N/A')
    number_of_seasons = data.get('number_of_seasons', 'N/A')
    original_name = data.get('original_name', 'N/A')
    popularity = data.get('popularity', 'N/A')

    # Return all the details
    return {
        'poster': full_poster_path,
        'overview': overview,
        'first_air_date': first_air_date,
        'last_air_date': last_air_date,
        'name': name,
        'number_of_episodes': number_of_episodes,
        'number_of_seasons': number_of_seasons,
        'original_name': original_name,
        'popularity': popularity
    }

# Function to recommend K-Dramas
def recommend(kdrama_name):
    # Find the index of the selected K-Drama
    index = kdrama[kdrama['name'] == kdrama_name].index[0]

    # Sort the K-Dramas based on similarity scores
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_kd_names = []
    recommended_kd_posters = []
    tmdb_ids = []

    # Fetch poster for top 5 similar K-Dramas
    for i in distances[1:6]:
        tmdb_id = kdrama.iloc[i[0]].tmdb_id
        details = fetch_poster_and_details(tmdb_id)
        recommended_kd_posters.append(details['poster'])
        recommended_kd_names.append(kdrama.iloc[i[0]]['name'])
        tmdb_ids.append(tmdb_id)

    return recommended_kd_names, recommended_kd_posters, tmdb_ids

@app.route('/', methods=['GET', 'POST'])
def index():
    kd_list = kdrama['name'].values
    selected_kd = None
    recommended_kd_names = []
    recommended_kd_posters = []
    tmdb_ids = []

    if request.method == 'POST':
        selected_kd = request.form.get('kd_selection')
        if selected_kd:
            recommended_kd_names, recommended_kd_posters, tmdb_ids = recommend(selected_kd)

    return render_template('index.html', kd_list=kd_list, selected_kd=selected_kd,
                           recommended_kd_names=recommended_kd_names,
                           recommended_kd_posters=recommended_kd_posters, tmdb_ids=tmdb_ids, zip=zip)

@app.route('/<int:tmdb_id>')
def kdrama_detail(tmdb_id):
    details = fetch_poster_and_details(tmdb_id)
    return render_template('kdrama_detail.html',
                           poster=details['poster'],
                           overview=details['overview'],
                           first_air_date=details['first_air_date'],
                           last_air_date=details['last_air_date'],
                           name=details['name'],
                           original_name=details['original_name'],
                           number_of_episodes=details['number_of_episodes'],
                           number_of_seasons=details['number_of_seasons'],
                           popularity=details['popularity'])

if __name__ == '__main__':
    app.run(debug=True)