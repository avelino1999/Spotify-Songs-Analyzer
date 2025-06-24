import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


# --- DATABASE CONNECTION FUNCTIONS ---

def connect_to_db(db_name):
    """
    Establish a connection to the SQLite database.

    Parameters:
        db_name (str): The name of the database file.

    Returns:
        conn: A SQLite connection object.
    """
    return sqlite3.connect(db_name)


# --- ARTIST VALIDATION FUNCTIONS ---

def validate_artist(conn, artist_name):
    """
    Validate whether the provided artist name exists in the database.

    Parameters:
        conn: The database connection object.
        artist_name (str): The name of the artist to validate.

    Returns:
        bool: True if the artist exists, False otherwise.
    """
    query = """
    SELECT COUNT(*) as count
    FROM Artist
    WHERE Artist.ArtistName = ?
    """
    result = pd.read_sql_query(query, conn, params=(artist_name,))
    return result['count'].iloc[0] > 0  # Returns True if the artist exists


# --- ARTIST DATA RETRIEVAL FUNCTIONS ---

def get_artist_data(conn, artist_name):
    """
    Retrieve artist-specific data, including genre-based popularity comparisons.

    Parameters:
        conn: The database connection object.
        artist_name (str): The name of the artist to retrieve data for.

    Returns:
        pd.DataFrame: A DataFrame containing the artist's genre-based popularity comparison.
    """
    query = """
    WITH ArtistGenres AS (
        SELECT Genre.Genre, 
               AVG(CAST(Song.Popularity AS FLOAT)) AS avg_popularity_artist
        FROM Genre
        LEFT JOIN Song ON Song.GenreID = Genre.ID
        LEFT JOIN Artist ON Song.ArtistID = Artist.ID
        WHERE Artist.ArtistName = ?
          AND Song.Popularity IS NOT NULL 
          AND Song.Popularity > 0
        GROUP BY Genre.Genre
    ),
    OverallGenres AS (
        SELECT Genre.Genre,
               AVG(CAST(Song.Popularity AS FLOAT)) AS avg_popularity_overall
        FROM Genre
        LEFT JOIN Song ON Song.GenreID = Genre.ID
        WHERE Song.Popularity IS NOT NULL
          AND Song.Popularity > 0
        GROUP BY Genre.Genre
    )
    SELECT og.Genre, 
           COALESCE(ag.avg_popularity_artist, 0) AS avg_popularity_artist, 
           og.avg_popularity_overall
    FROM OverallGenres og
    LEFT JOIN ArtistGenres ag ON og.Genre = ag.Genre
    """
    result = pd.read_sql_query(query, conn, params=(artist_name,))
    return result


# --- GENRE AVERAGE RETRIEVAL FUNCTIONS ---

def get_genre_average(conn):
    """
    Retrieve the overall average popularity for each genre.

    Parameters:
        conn: The database connection object.

    Returns:
        pd.DataFrame: A DataFrame with genre-based average popularity values.
    """
    query = """
    SELECT Genre.Genre, 
           COALESCE(AVG(CAST(Song.Popularity AS FLOAT)), 0) AS avg_popularity
    FROM Genre
    LEFT JOIN Song ON Song.GenreID = Genre.ID
    WHERE Song.Popularity IS NOT NULL
      AND Song.Popularity > 0
    GROUP BY Genre.Genre
    """
    return pd.read_sql_query(query, conn)


# --- DATA PREPROCESSING FUNCTIONS ---

def split_and_aggregate(data):
    """
    Split multi-genre entries into separate rows and aggregate the average popularity for each genre.

    Parameters:
        data (pd.DataFrame): The raw artist genre data to process.

    Returns:
        pd.DataFrame: A DataFrame with aggregated average popularity for each genre.
    """
    rows = []
    
    # Process each row in the data
    for _, row in data.iterrows():
        genres = row['Genre'].split(', ')  # Assuming multiple genres are stored as a comma-separated string
        for genre in genres:
            rows.append({
                'Genre': genre, 
                'avg_popularity_artist': row['avg_popularity_artist'], 
                'avg_popularity_overall': row['avg_popularity_overall']
            })
    
    # Create DataFrame and aggregate
    df = pd.DataFrame(rows)
    return df.groupby('Genre', as_index=False).mean()


# --- DATA DISPLAY FUNCTIONS ---

def display_table(artist_data):
    """
    Display the results in a tabular format with a comparison column.

    Parameters:
        artist_data (pd.DataFrame): The processed artist data to display.
    """
    # Add a new column to indicate whether the artist's popularity is above the overall average
    artist_data['Above Overall Avg'] = artist_data['avg_popularity_artist'] > artist_data['avg_popularity_overall']
    
    # Display the table with formatted columns
    print(f"{'Genre':<20} {'Artist Avg Popularity':<25} {'Overall Avg Popularity':<25} {'Above Overall Avg'}")
    print("-" * 75)
    
    # Iterate through rows and print values
    for index, row in artist_data.iterrows():
        above_overall = "Yes" if row['Above Overall Avg'] else "No"
        print(f"{row['Genre']:<20} {row['avg_popularity_artist']:<25.2f} {row['avg_popularity_overall']:<25.2f} {above_overall}")


# --- PLOTTING FUNCTIONS ---

def plot_data(artist_data, genre_avg):
    """
    Plot a bar chart comparing the artist's popularity with overall genre popularity.

    Parameters:
        artist_data (pd.DataFrame): The processed artist data.
        genre_avg (pd.DataFrame): The overall genre average popularity data.
    """
    # Merge artist and genre data
    merged_data = pd.merge(artist_data, genre_avg, on='Genre', how='left', suffixes=('_artist', '_overall'))
    
    # Plot settings
    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    index = range(len(merged_data))
    
    # Create bars for artist and overall popularity
    plt.bar(index, merged_data['avg_popularity_artist'], bar_width, label='Artist Avg Popularity')
    plt.bar([i + bar_width for i in index], merged_data['avg_popularity_overall'], bar_width, label='Overall Avg Popularity')
    
    # Formatting
    plt.xlabel('Genres')
    plt.ylabel('Popularity')
    plt.title('Artist Popularity vs Overall Genre Popularity')
    plt.xticks([i + bar_width / 2 for i in index], merged_data['Genre'], rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # Show plot
    plt.show()


# --- TESTING FUNCTIONS ---

def get_first_artist_name(conn):
    """
    Fetch the first artist name from the database for testing purposes.

    Parameters:
        conn: The database connection object.

    Returns:
        str: The name of the first artist or None if no artists are found.
    """
    query = "SELECT ArtistName FROM Artist LIMIT 1"
    result = pd.read_sql_query(query, conn)
    if not result.empty:
        return result.iloc[0]['ArtistName']
    return None


# --- UNIT TESTS ---

def test_connect_to_db():
    """Test the database connection function."""
    conn = connect_to_db('CWDatabase.db')
    assert conn is not None
    print("test_connect_to_db passed.")
    conn.close()


def test_validate_artist():
    """Test the artist validation function."""
    conn = connect_to_db('CWDatabase.db')
    artist_name = get_first_artist_name(conn)
    if artist_name:
        assert validate_artist(conn, artist_name) == True  # Use actual artist name
        assert validate_artist(conn, 'Unknown Artist') == False
        print("test_validate_artist passed.")
    else:
        print("No artist found in the database for testing.")
    conn.close()


def test_get_artist_data():
    """Test the artist data retrieval function."""
    conn = connect_to_db('CWDatabase.db')
    artist_name = get_first_artist_name(conn)
    if artist_name:
        artist_data = get_artist_data(conn, artist_name)
        assert not artist_data.empty
        print("test_get_artist_data passed.")
    else:
        print("No artist found in the database for testing.")
    conn.close()


def test_get_genre_average():
    """Test the genre average retrieval function."""
    conn = connect_to_db('CWDatabase.db')
    genre_avg = get_genre_average(conn)
    assert not genre_avg.empty
    print("test_get_genre_average passed.")
    conn.close()


# --- MAIN FUNCTION ---

if __name__ == '__main__':
    # Run all tests
    test_connect_to_db()
    test_validate_artist()
    test_get_artist_data()
    test_get_genre_average()
