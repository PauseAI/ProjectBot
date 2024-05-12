from airtable_client import TABLES
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, date

def plot_arrivals(data, source: str, date_field: str = "Datetime Joined", per_week: bool = False):
    # Assuming the data is stored in a variable called 'data'
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data)

    # Extract the 'Datetime Joined' field and convert it to a datetime object
    df['Datetime Joined'] = pd.to_datetime(df['fields'].apply(lambda x: x[date_field]))
    df = df[df["Datetime Joined"].dt.date > date(2023, 11, 1)]

    if per_week:
        # Group the data by week and count the number of people joining each week
        weekly_counts = df.groupby(pd.Grouper(key='Datetime Joined', freq='W')).size().reset_index(name='count')
        weekly_counts['Datetime Joined'] = weekly_counts['Datetime Joined'].dt.date
        # Calculate the 7-week moving average
        weekly_counts['moving_average'] = weekly_counts['count'].rolling(window=4).mean()

        # Create a bar chart with a line for the moving average
        plt.figure(figsize=(10, 6))
        plt.bar(weekly_counts['Datetime Joined'], weekly_counts['count'], label='Weekly Joins')
        plt.plot(weekly_counts['Datetime Joined'], weekly_counts['moving_average'], color='red', label='4-Week Moving Average')
        plt.xlabel('Week')
        plt.ylabel('Number of People Joining')
        plt.title(f'Weekly {source} Joins')
    else:
        # Group the data by date and count the number of people joining each day
        daily_counts = df.groupby(df['Datetime Joined'].dt.date).size().reset_index(name='count')

        # Calculate the 7-day moving average
        daily_counts['moving_average'] = daily_counts['count'].rolling(window=7).mean()

        # Create a bar chart with a line for the moving average
        plt.figure(figsize=(10, 6))
        plt.bar(daily_counts['Datetime Joined'], daily_counts['count'], label='Daily Joins')
        plt.plot(daily_counts['Datetime Joined'], daily_counts['moving_average'], color='red', label='7-Day Moving Average')
        plt.xlabel('Date')
        plt.ylabel('Number of People Joining')
        plt.title(f'Daily {source} Joins')

    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # plt.show()
    # Save the figure to a file
    plt.savefig(f'plots/{source}_joins_plot.png', dpi=300)