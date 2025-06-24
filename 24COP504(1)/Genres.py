import pandas as pd
import sqlite3
import matplotlib.pyplot as plt


# --- USER INPUT FUNCTION ---

def input_year():
    """
    Prompt the user to input a year between 1998 and 2020.

    Continuously asks for input until a valid year is provided. If the input is invalid
    (non-integer or out of range), it will prompt the user again.

    Returns:
        int: The valid year entered by the user.
    """
    while True:
        try:
            a = int(input("Enter a year: "))
            
            # Check if the year is in the valid range
            if 1998 <= a <= 2020:
                print(f"Songs in Year {a}")
                return a  # Return the valid year
            else:
                print("The number is not in the range. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid year.")


# --- DATA FETCHING AND PLOTTING FUNCTION ---

def fetch_year_summary_and_plot(year):
    """
    Fetch the summary of song data for the given year and plot the distribution of songs by genre.

    The function performs the following steps:
    1. Fetches aggregated data (Danceability, Duration, Popularity) per genre for the specified year.
    2. Displays the data in a tabular format.
    3. Plots a pie chart showing the distribution of total songs across genres.

    Parameters:
        year (int): The year for which to fetch the summary.
    """
    # Connect to the database
    conn = sqlite3.connect('CWDatabase.db')

    # Define the query with aggregation for additional fields (Danceability, Duration, Popularity, and Total Songs)
    query = '''
        SELECT a.Genre, 
               AVG(b.Danceability) AS AvgDanceability,
               AVG(b.Duration) AS AvgDuration,
               AVG(b.Popularity) AS AvgPopularity,
               COUNT(b.ID) AS TotalSongs
        FROM Genre a
        LEFT JOIN Song b ON a.ID = b.GenreID
        WHERE b.Year = ?
        GROUP BY a.Genre
    '''
    
    # Execute the query and fetch results into a DataFrame
    dfSummary = pd.read_sql_query(query, conn, params=(year,))
    conn.close()

    # If no data is returned, inform the user
    if dfSummary.empty:
        print(f"No data available for the year {year}.")
    else:
        # Split genres into separate rows if multiple genres exist in a single entry
        dfSummary['Genre'] = dfSummary['Genre'].str.split(', ')
        dfSummary = dfSummary.explode('Genre')
        
        # Aggregate by unique genres
        dfSummary = dfSummary.groupby('Genre').agg({
            'AvgDanceability': 'mean',
            'AvgDuration': 'mean',
            'AvgPopularity': 'mean',
            'TotalSongs': 'sum'
        }).reset_index()

        # Display the summary in a clean tabular format
        print(dfSummary.to_string(index=False, col_space=20, justify='left', float_format="{:.3f}".format))

        # Plot a pie chart for the total number of songs per genre
        plt.figure(figsize=(8, 6))
        plt.pie(dfSummary['TotalSongs'], labels=dfSummary['Genre'], autopct='%1.1f%%', startangle=140)
        plt.title(f"Distribution of Total Songs by Genre in {year}")
        plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
        plt.legend(title="Genres")
        plt.show()


# --- TEST FUNCTIONS ---

def test_valid_year_input():
    """
    Test the valid year input function.

    Mocks user input to simulate entering a valid year and verifies that the function returns it.
    """
    import builtins
    builtins.input = lambda _: '2010'  # Mocking input for the year 2010
    assert input_year() == 2010
    print("test_valid_year_input passed.")


def test_invalid_year_input():
    """
    Test the invalid year input function.

    Mocks multiple user inputs to simulate invalid year entries and verifies that the function
    returns the last valid input.
    """
    import builtins
    inputs = iter(['1995', '2025', '2005'])  # Mocking a sequence of invalid inputs followed by a valid one
    builtins.input = lambda _: next(inputs)
    assert input_year() == 2005
    print("test_invalid_year_input passed.")


def test_fetch_year_summary_no_data():
    """
    Test fetching year summary when no data is available for the year.

    Calls the function with a year (1999) that is assumed to have no data and prints a confirmation message.
    """
    fetch_year_summary_and_plot(1999)  # Assumes 1999 has no data
    print("test_fetch_year_summary_no_data executed.")


def test_fetch_year_summary_with_data():
    """
    Test fetching year summary when data is available for the year.

    Calls the function with a year (2010) that is assumed to have data and prints a confirmation message.
    """
    fetch_year_summary_and_plot(2010)  # Assumes 2010 has data
    print("test_fetch_year_summary_with_data executed.")


# --- MAIN FUNCTION ---

if __name__ == "__main__":
    # Execute all tests to validate the functionality
    test_valid_year_input()
    test_invalid_year_input()
    test_fetch_year_summary_no_data()
    test_fetch_year_summary_with_data()
