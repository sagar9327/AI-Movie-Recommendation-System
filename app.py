import streamlit as st
import pickle
import joblib
import requests
from pathlib import Path


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Movie Explorer",
    page_icon="🎬",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       PAGE
       ===================================================== */

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }


    /* =====================================================
       APP TITLE
       ===================================================== */

    .app-title {
        font-size: 42px;
        font-weight: 700;
        line-height: 1.15;
        margin: 0;
        padding: 0;
    }

    .app-description {
        font-size: 16px;
        color: #555555;
        margin-top: 8px;
        margin-bottom: 12px;
    }


    /* =====================================================
       SECTION TITLE
       ===================================================== */

    .section-title {
        font-size: 30px;
        font-weight: 700;
        line-height: 1.2;
        margin-top: 8px;
        margin-bottom: 12px;
    }


    /* =====================================================
       SEARCH
       ===================================================== */

    div[data-testid="stTextInput"] {
        margin-bottom: 8px;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 10px;
        padding: 12px;
        font-size: 16px;
    }


    /* =====================================================
       POSTER FRAME
       ===================================================== */

    .poster-frame {
        width: 240px;
        height: 360px;

        margin: 0 auto;

        background-color: #f1f1f1;

        border-radius: 10px;

        display: flex;
        align-items: center;
        justify-content: center;

        overflow: hidden;
    }


    /* =====================================================
       POSTER IMAGE
       ===================================================== */

    .poster-frame img {
        width: 240px;
        height: 360px;

        object-fit: contain;

        display: block;

        border-radius: 10px;
    }


    /* =====================================================
       POSTER FALLBACK
       ===================================================== */

    .poster-placeholder {
        width: 240px;
        height: 360px;

        background-color: #eeeeee;

        border-radius: 10px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 55px;
    }


    /* =====================================================
       MOVIE TITLE
       ===================================================== */

    .movie-title {
        height: 58px;

        font-size: 18px;
        font-weight: 700;
        line-height: 1.35;

        margin-top: 12px;
        margin-bottom: 4px;

        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;

        overflow: hidden;
    }


    /* =====================================================
       YEAR
       ===================================================== */

    .movie-year {
        height: 28px;

        font-size: 14px;
        color: #777777;

        display: flex;
        align-items: center;
    }


    /* =====================================================
       RATING
       ===================================================== */

    .movie-rating {
        height: 32px;

        font-size: 16px;
        font-weight: 600;

        display: flex;
        align-items: center;
    }


    /* =====================================================
       GENRE
       ===================================================== */

    .movie-genre {
        height: 44px;

        font-size: 14px;
        color: #777777;
        line-height: 1.4;

        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;

        overflow: hidden;
    }


    /* =====================================================
       BUTTON
       ===================================================== */

    div.stButton > button {
        min-width: 145px;
        min-height: 40px;

        padding: 7px 15px;

        border-radius: 8px;

        white-space: nowrap;

        font-size: 15px;
    }


    /* =====================================================
       DETAIL PAGE
       ===================================================== */

    .detail-title {
        font-size: 38px;
        font-weight: 700;
        line-height: 1.2;

        margin-top: 10px;
        margin-bottom: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# LOAD MOVIE DATA
# =========================================================

with open(BASE_DIR / "movies.pickle", "rb") as file:
    movies = pickle.load(file)


similarity = joblib.load(
    BASE_DIR / "similarity.joblib"
)


# =========================================================
# OMDB CONFIGURATION
# =========================================================

OMDB_API_KEY = st.secrets["OMDB_API_KEY"]

OMDB_URL = "https://www.omdbapi.com/"


# =========================================================
# SESSION STATE
# =========================================================

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None


# =========================================================
# OMDB API
# =========================================================

@st.cache_data(ttl=86400)
def get_movie_details(movie_title):

    params = {
        "apikey": OMDB_API_KEY,
        "t": movie_title,
        "type": "movie"
    }

    try:

        response = requests.get(
            OMDB_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if data.get("Response") == "True":
            return data

        return None

    except requests.RequestException:

        return None


# =========================================================
# RECOMMENDATION ENGINE
# =========================================================

def recommend(movie_title, number_of_movies=6):

    movie_index = movies[
        movies["title"] == movie_title
    ].index[0]

    recommendations = similarity[movie_index]

    movie_list = sorted(
        enumerate(recommendations),
        reverse=True,
        key=lambda x: x[1]
    )[1:number_of_movies + 1]

    recommended_movies = []

    for index, score in movie_list:

        recommended_movies.append(
            movies.iloc[index]["title"]
        )

    return recommended_movies


# =========================================================
# GET MOVIE
# =========================================================

def get_movie(movie_title):

    return movies[
        movies["title"] == movie_title
    ].iloc[0]


# =========================================================
# SHOW FIXED POSTER
# =========================================================

def show_poster(movie_data):

    if movie_data:

        poster = movie_data.get("Poster")

        if poster and poster != "N/A":

            st.markdown(
                f"""
                <div class="poster-frame">
                    <img
                        src="{poster}"
                        alt="Movie Poster"
                    >
                </div>
                """,
                unsafe_allow_html=True
            )

            return

    # -----------------------------------------------------
    # FALLBACK
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="poster-placeholder">
            🎬
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# MOVIE CARD
# =========================================================

def movie_card(movie_title, card_index):

    movie_data = get_movie_details(movie_title)

    # -----------------------------------------------------
    # CARD
    # -----------------------------------------------------

    with st.container(border=True):

        # -------------------------------------------------
        # POSTER
        # -------------------------------------------------

        show_poster(movie_data)

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        st.markdown(
            f"""
            <div class="movie-title">
                {movie_title}
            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # DEFAULT VALUES
        # -------------------------------------------------

        year = ""

        rating = ""

        genre = ""

        if movie_data:

            year = movie_data.get(
                "Year",
                ""
            )

            rating = movie_data.get(
                "imdbRating",
                ""
            )

            genre = movie_data.get(
                "Genre",
                ""
            )

        # -------------------------------------------------
        # YEAR
        # -------------------------------------------------

        if year and year != "N/A":

            year_text = f"📅 {year}"

        else:

            year_text = ""

        st.markdown(
            f"""
            <div class="movie-year">
                {year_text}
            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # RATING
        # -------------------------------------------------

        if rating and rating != "N/A":

            rating_text = f"⭐ IMDb {rating}"

        else:

            rating_text = ""

        st.markdown(
            f"""
            <div class="movie-rating">
                {rating_text}
            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # GENRE
        # -------------------------------------------------

        if genre and genre != "N/A":

            genre_text = f"🎭 {genre}"

        else:

            genre_text = ""

        st.markdown(
            f"""
            <div class="movie-genre">
                {genre_text}
            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # BUTTON
        # -------------------------------------------------

        if st.button(
            "View Movie →",
            key=f"view_{movie_title}_{card_index}"
        ):

            st.session_state.selected_movie = movie_title

            st.rerun()


# =========================================================
# MOVIE DETAILS PAGE
# =========================================================

def show_movie_details(movie_title):

    movie = get_movie(movie_title)

    movie_data = get_movie_details(movie_title)

    # -----------------------------------------------------
    # BACK BUTTON
    # -----------------------------------------------------

    if st.button(
        "← Back to Movies",
        key="back_to_movies"
    ):

        st.session_state.selected_movie = None

        st.rerun()

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    st.markdown(
        f"""
        <div class="detail-title">
            {movie_title}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------------------------------
    # POSTER + DETAILS
    # -----------------------------------------------------

    poster_column, details_column = st.columns(
        [1, 2]
    )

    # -----------------------------------------------------
    # POSTER
    # -----------------------------------------------------

    with poster_column:

        show_poster(movie_data)

    # -----------------------------------------------------
    # DETAILS
    # -----------------------------------------------------

    with details_column:

        if movie_data:

            rating = movie_data.get(
                "imdbRating"
            )

            year = movie_data.get(
                "Year"
            )

            runtime = movie_data.get(
                "Runtime"
            )

            genre = movie_data.get(
                "Genre"
            )

            director = movie_data.get(
                "Director"
            )

            actors = movie_data.get(
                "Actors"
            )

            released = movie_data.get(
                "Released"
            )

            rated = movie_data.get(
                "Rated"
            )

            votes = movie_data.get(
                "imdbVotes"
            )

            metascore = movie_data.get(
                "Metascore"
            )

            # IMDb rating

            if rating and rating != "N/A":

                st.metric(
                    "⭐ IMDb Rating",
                    f"{rating}/10"
                )

            col1, col2 = st.columns(2)

            with col1:

                if year and year != "N/A":

                    st.write(
                        f"📅 **Year:** {year}"
                    )

                if released and released != "N/A":

                    st.write(
                        f"🎬 **Released:** {released}"
                    )

                if runtime and runtime != "N/A":

                    st.write(
                        f"⏱️ **Runtime:** {runtime}"
                    )

                if rated and rated != "N/A":

                    st.write(
                        f"🔞 **Rated:** {rated}"
                    )

            with col2:

                if genre and genre != "N/A":

                    st.write(
                        f"🎭 **Genre:** {genre}"
                    )

                if director and director != "N/A":

                    st.write(
                        f"🎥 **Director:** {director}"
                    )

                if votes and votes != "N/A":

                    st.write(
                        f"👤 **Votes:** {votes}"
                    )

                if metascore and metascore != "N/A":

                    st.write(
                        f"📊 **Metascore:** {metascore}"
                    )

            # Cast

            if actors and actors != "N/A":

                st.write(
                    f"👥 **Cast:** {actors}"
                )

        else:

            st.warning(
                "Movie details could not be loaded from OMDb."
            )

    # =====================================================
    # OVERVIEW
    # =====================================================

    st.divider()

    st.header("📝 Overview")

    if movie_data:

        plot = movie_data.get(
            "Plot"
        )

        if plot and plot != "N/A":

            st.write(plot)

        else:

            dataset_plot = movie.get(
                "overview"
            )

            if dataset_plot:

                st.write(dataset_plot)

    else:

        dataset_plot = movie.get(
            "overview"
        )

        if dataset_plot:

            st.write(dataset_plot)

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    st.divider()

    st.header("🎯 You May Also Like")

    recommendations = recommend(
        movie_title,
        number_of_movies=6
    )

    columns = st.columns(3)

    for index, recommendation in enumerate(
        recommendations
    ):

        with columns[index % 3]:

            movie_card(
                recommendation,
                f"recommendation_{index}"
            )


# =========================================================
# HOME PAGE
# =========================================================

def show_home():

    # -----------------------------------------------------
    # APP HEADER
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="app-title">
            🎬 AI Movie Explorer
        </div>

        <div class="app-description">
            Discover movies and find similar movies
            using AI-powered content-based recommendations.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="section-title">
            🔍 Search Movies
        </div>
        """,
        unsafe_allow_html=True
    )

    movie_names = movies[
        "title"
    ].tolist()

    search = st.text_input(
        "Search",
        placeholder="Search for a movie..."
    )

    # -----------------------------------------------------
    # SEARCH RESULTS
    # -----------------------------------------------------

    if search:

        filtered_movies = [

            movie
            for movie in movie_names

            if search.lower() in movie.lower()

        ]

        if filtered_movies:

            st.write(
                f"Found {len(filtered_movies)} movies"
            )

            columns = st.columns(3)

            for index, movie in enumerate(
                filtered_movies[:12]
            ):

                with columns[index % 3]:

                    movie_card(
                        movie,
                        f"search_{index}"
                    )

        else:

            st.warning(
                "No movies found."
            )

    # -----------------------------------------------------
    # EXPLORE MOVIES
    # -----------------------------------------------------

    else:

        st.markdown(
            """
            <div class="section-title">
                🍿 Explore Movies
            </div>
            """,
            unsafe_allow_html=True
        )

        columns = st.columns(3)

        for index, movie in enumerate(
            movie_names[:12]
        ):

            with columns[index % 3]:

                movie_card(
                    movie,
                    f"home_{index}"
                )


# =========================================================
# APP ROUTING
# =========================================================

if st.session_state.selected_movie:

    show_movie_details(
        st.session_state.selected_movie
    )

else:

    show_home()