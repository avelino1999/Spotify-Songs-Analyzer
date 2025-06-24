import pandas as pd
import sqlite3
import matplotlib.pyplot as plt


# --- DATABASE CONNECTION FUNCTION ---

def connect_to_db(db_name):
    """
    Connect to the SQLite database.

    Parameters:
        db_name (str): The name of the SQLite database file.

    Returns:
        conn (sqlite3.Connection): The connection object to the database.
    """
    return sqlite3.connect(db_name)


# --- YEAR VALIDATION FUNCTION ---

def validate_years(start_year, end_year):
    """
    Validate that the input years are within the acceptable range (1998-2020).

    Parameters:
        start_year (int): The starting year.
        end_year (int): The ending year.

    Returns:
        bool: True if the years are valid, False otherwise.
    """
    if start_year < 1998 or end_year > 2020 or start_year > end_year:
        return False
    return True


# --- DATA RETRIEVAL AND PROCESSING FUNCTIONS ---

def get_artist_data(conn, start_year, end_year):
    """
    Retrieve the data for artists within the specified year range.

    Parameters:
        conn (sqlite3.Connection): The connection object to the database.
        start_year (int): The starting year.
        end_year (int): The ending year.

    Returns:
        pd.DataFrame: DataFrame containing artist data with song counts and average popularity.
    """
    query = """
    SELECT Artist.ArtistName, Song.Year, COUNT(Song.ID) AS num_songs, AVG(Song.Popularity) AS avg_popularity
    FROM Song
    JOIN Artist ON Song.ArtistID = Artist.ID
    WHERE Song.Year BETWEEN ? AND ?
    GROUP BY Artist.ArtistName, Song.Year
    """
    return pd.read_sql_query(query, conn, params=(start_year, end_year))


def calculate_rank_value(data, weight_x=0.5, weight_y=0.5):
    """
    Calculate the rank value for each artist based on the number of songs and average popularity.

    Parameters:
        data (pd.DataFrame): The artist data with song counts and popularity.
        weight_x (float): The weight for the number of songs.
        weight_y (float): The weight for the average popularity.

    Returns:
        pd.DataFrame: The data with an additional column 'rank_value' representing the rank.
    """
    data['rank_value'] = (data['num_songs'] * weight_x) + (data['avg_popularity'] * weight_y)
    return data


def get_top_artists(data, top_n=5):
    """
    Identify the top artists based on the average rank value.

    Parameters:
        data (pd.DataFrame): The artist data with rank values.
        top_n (int): The number of top artists to retrieve.

    Returns:
        pd.DataFrame: DataFrame containing the top N artists based on their rank values.
    """
    data['avg_rank_value'] = data.groupby('ArtistName')['rank_value'].transform('mean')
    top_artists = data.sort_values(by='avg_rank_value', ascending=False).drop_duplicates('ArtistName').head(top_n)
    return data[data['ArtistName'].isin(top_artists['ArtistName'])]


# --- DISPLAY AND PLOTTING FUNCTIONS ---

def display_table(data):
    """
    Display the results in a tabular format using Pandas.

    Parameters:
        data (pd.DataFrame): The artist data with popularity for each year.

    Returns:
        pd.DataFrame: The pivoted table with artists as rows, years as columns, and average popularity as values.
    """
    # Print the column names of the dataset to check for any discrepancies
    print("Columns in the dataset:", data.columns)
    
    # Pivot the data: ArtistName as rows, Years as columns, avg_popularity as values
    pivot_data = data.pivot_table(index='ArtistName', columns='Year', values='avg_popularity', aggfunc='mean')

    # Check if pivot_data is correctly formed
    print("Pivoted data:\n", pivot_data)
    
    # Fill NaN values with 'Null' to represent missing values in the table
    pivot_data = pivot_data.where(pd.notnull(pivot_data), 'Null')
    
    # Return the pivoted table to allow further styling
    return pivot_data

    # Calculate the average for each artist across all years (excluding 'Null' values)
    def calculate_average(row):
        # Exclude 'Null' values before calculating the mean
        numeric_values = row[row != 'Null']
        if len(numeric_values) > 0:
            return numeric_values.mean()
        else:
            return 'Null'
    
    # Add the "Average" column to the pivoted table
    pivot_data['Average'] = pivot_data.apply(calculate_average, axis=1)

    # Sort the data by the "Average" column in descending order
    pivot_data = pivot_data.sort_values(by='Average', ascending=False)

    # Display the final table
    print(pivot_data)  # For testing, use print to view the result
    return pivot_data


def plot_data(data):
    """
    Plot a line chart comparing the yearly rank values with the average.

    Parameters:
        data (pd.DataFrame): The artist data with rank values for each year.
    """
    pivot_data = data.pivot(index='Year', columns='ArtistName', values='rank_value')
    
    # Plot the data
    ax = pivot_data.plot(marker='o', figsize=(10, 6))
    
    # Calculate and plot the average rank value per year
    avg_rank_value = pivot_data.mean(axis=1)
    avg_rank_value.plot(ax=ax, marker='o', color='red', linestyle='-', label='Average')
    
    plt.xlabel('Year')
    plt.ylabel('Rank Value')
    plt.title('Yearly Rank Values for Top Artists')
    plt.legend(title='Artist')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# --- MAIN FUNCTION TO GET TOP 5 ARTISTS AND PLOT ---

def get_top_5_artists_by_year_range(start_year, end_year):
    """
    Get the top 5 artists within the specified year range.

    Parameters:
        start_year (int): The starting year.
        end_year (int): The ending year.
    
    Returns:
        pd.DataFrame: The top 5 artists' data, including rank values and popularity.
    """
    conn = connect_to_db('CWDatabase.db')
    artist_data = get_artist_data(conn, start_year, end_year)
    conn.close()

    if artist_data.empty:
        print(f"No data found for the years {start_year}-{end_year}.")
        return None

    artist_data = calculate_rank_value(artist_data)
    top_artists_data = get_top_artists(artist_data)

    display_table(top_artists_data)
    plot_data(top_artists_data)


def plot_top_5_artists_rank_values(start_year, end_year):
    """
    Plot the top 5 artists' rank values over the specified year range.

    Parameters:
        start_year (int): The starting year.
        end_year (int): The ending year.
    """
    top_5_artists = get_top_5_artists_by_year_range(start_year, end_year)
    
    if top_5_artists is None:
        return

    print(f"\nTop 5 artists from {start_year} to {end_year} (Avg Popularity by Year):")
    print(top_5_artists)

    # Plotting the graph
    plt.figure(figsize=(10, 6))

    for artist in top_5_artists['ArtistName'].unique():
        artist_data = top_5_artists[top_5_artists['ArtistName'] == artist]
        plt.plot(artist_data['Year'], artist_data['rank_value'], label=artist, marker='o')

    # Calculate and plot the average rank value per year
    avg_rank_values = top_5_artists.groupby('Year')['rank_value'].mean()
    plt.plot(avg_rank_values.index, avg_rank_values, label='Average Rank Value', color='black', linestyle='--', marker='x')

    plt.xlabel("Year")
    plt.ylabel("Avg Popularity")
    plt.title(f"Yearly Rank Values for Top 5 Artists ({start_year} - {end_year})")
    plt.legend()
    plt.grid(True)
    plt.xticks(range(start_year, end_year + 1))

    plt.show()


# --- TESTING FUNCTIONS ---

def test_functions():
    """
    Test the functions with sample data.

    This function validates the year range, database connection, and data retrieval.
    """
    # Test validation of years
    assert validate_years(2000, 2010) == True
    assert validate_years(1997, 2010) == False
    assert validate_years(2000, 2021) == False
    assert validate_years(2015, 2010) == False
    print("Year validation tests passed.")

    # Test connection to the database
    try:
        conn = connect_to_db('CWDatabase.db')
        assert conn is not None
        conn.close()
        print("Database connection test passed.")
    except Exception as e:
        print(f"Database connection test failed: {e}")

    # Test data retrieval and processing
    conn = connect_to_db('CWDatabase.db')
    artist_data = get_artist_data(conn, 2000, 2010)
    assert not artist_data.empty, "Data retrieval failed"
    artist_data = calculate_rank_value(artist_data)
    top_artists_data = get_top_artists(artist_data)
    assert not top_artists_data.empty, "Top artists data is empty"
    conn.close()
    print("Data retrieval and processing tests passed.")


# --- MAIN EXECUTION ---

if __name__ == '__main__':
    test_functions()

    # Input years for the plot
    start_year = int(input("Enter the start year (1998-2020): "))
    end_year = int(input("Enter the end year (1998-2020): "))

    # Validate input years
    if validate_years(start_year, end_year):
        plot_top_5_artists_rank_values(start_year, end_year)
    else:
        print("Invalid input. Please enter years between 1998 and 2020, with the start year being less than or equal to the end year.")
