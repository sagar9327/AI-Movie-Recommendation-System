# 🎬 AI Movie Recommendation System

An AI-powered movie recommendation system built using **Python, Pandas, Scikit-learn, and Streamlit**.

The application uses **content-based filtering** and **cosine similarity** to recommend movies that are similar to a movie selected by the user.

---

## 🚀 Features

- 🎬 Search and select a movie
- 🤖 Content-based movie recommendations
- 🔍 Uses movie metadata to calculate similarity
- 📊 Cosine similarity for recommendation ranking
- ⚡ Fast recommendations using a precomputed similarity matrix
- 🌐 Interactive Streamlit web interface
- 📱 Simple and responsive UI

---

## 🛠️ Tech Stack

- **Python**
- **Pandas**
- **NumPy**
- **Scikit-learn**
- **Streamlit**
- **Joblib**
- **NLTK**
- **TMDB Dataset**

---

## 🧠 How It Works

The recommendation system follows a content-based filtering approach.

### 1. Movie Dataset

The project uses the **TMDB 5000 Movies** and **TMDB 5000 Credits** datasets.

Movie information includes:

- Genres
- Keywords
- Overview
- Cast
- Crew
- Movie title

### 2. Feature Preparation

Relevant movie information is combined into a single feature representation.

For example:

```text
Action Adventure Superhero Marvel Robert Downey Jr ...
