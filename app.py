import streamlit as st
import nltk
import sklearn
import pandas as pd
import pickle
import joblib
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity  

st.title("Movie Recommendation System")

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / 'movies.pickle', 'rb') as m:
    movies = pickle.load(m)

similarity = joblib.load(BASE_DIR /'similarity.joblib')
movie_names = movies['title'].values


def recommend(name_movie):
    movie_index = movies[movies['title'] == name_movie].index[0]
    
    recommendations = similarity[movie_index]
    movie_list = sorted(
        enumerate(recommendations),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]
    recommended_movies = []
    for i in movie_list:
        recommended_movies.append(movies.iloc[i[0]].title)
    return recommended_movies

name_movie = st.selectbox("Enter the movie name", movie_names)


if st.button("Recommend"):
    r = recommend(name_movie)
    for i in r:
        st.write(i)