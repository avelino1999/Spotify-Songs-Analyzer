# 🎵 Spotify Songs Analyzer (2000–2019)

This project is a data-driven analysis tool that explores the most popular songs on Spotify from 2000 to 2019. Built using **Python**, **pandas**, and **SQLite**, and run in a **Jupyter Notebook environment (Anaconda)**, the tool provides interactive insights into genre trends, artist popularity, and the evolution of music over two decades.

---

## 📂 Project Structure

| File / Folder            | Description |
|--------------------------|-------------|
| `menu.ipynb`             | Main Jupyter notebook that runs the UI interface using `ipywidgets`. Launch this to interact with the project. |
| `CWDatabase.db`          | SQLite database storing cleaned and structured song data for querying. |
| `songs.csv`              | Raw dataset sourced from [Kaggle's Top Hits Spotify (2000–2019)](https://www.kaggle.com/datasets/paradisejoy/top-hits-spotify-from-20002019). |
| `CW_Preprocessing.py`    | Script to preprocess the CSV and populate the SQLite database (`CWDatabase.db`). |
| `Artist.py`              | Contains functions to validate artists, calculate average popularity by genre, and compare with global genre averages. |
| `Genres.py`              | Contains logic to analyze and visualize genre popularity trends by year. |
| `Top5.py`                | Logic to identify and visualize the top 5 artists by popularity for selected year ranges. |
| `__pycache__/`           | Auto-generated cache directory for compiled Python files. Not needed for manual editing. |

---

## 🔧 Technologies Used

- **Python 3.10**
- **pandas** – for data analysis
- **SQLite3** – to store and query song data
- **Matplotlib** – for visualizations
- **ipywidgets** – for building interactive Jupyter UI
- **Jupyter Notebook** – development environment (via Anaconda)

---

## 🚀 How to Run

1. **Clone this repository:**
   ```bash
   git clone https://github.com/your-username/spotify-songs-analyzer.git
   cd spotify-songs-analyzer

   Open and run menu.ipynb to interact with the analyzer:

🎧 Genre: Explore popularity trends by year.

🎤 Artist: Enter an artist's name to see their genre-based popularity vs overall genre trends.

🏆 Top 5 Artists: Select year range to see the top 5 artists and their popularity over time.

📊 Features
Genre Analysis: Visualize average song popularity by genre across years.

Artist Breakdown: Compare an artist’s average popularity across genres vs overall genre popularity.

Top 5 Artists: Identify and highlight the most popular artists by year and across ranges.

Styled Tables: Dynamic highlighting of above-average performance and top values.

Interactive Dashboard: Widget-driven Jupyter notebook interface.

📌 Dataset Source
Top Hits Spotify from 2000–2019 - Kaggle
