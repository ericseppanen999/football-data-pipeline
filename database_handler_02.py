import requests
import psycopg2
import pandas as pd
from api_handler_01 import APIHandler
from dotenv import load_dotenv
import logging

logging.basicConfig(
    filename="application.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# initialize api handler
api_handler = APIHandler()

# define the leagues to fetch (league_id: league_name)
leagues = {
    39: "Premier League",
    140: "La Liga",
    135: "Serie A",
    78: "Bundesliga",
    61: "Ligue 1",
}

# connect to the database
postgres_connection = psycopg2.connect(
    dbname=api_handler.db_config["name"],
    user=api_handler.db_config["username"],
    password=api_handler.db_config["password"],
    host=api_handler.db_config["host"],
    port=api_handler.db_config["port"]
)
logging.info("Connected to PostgreSQL database successfully.")



cur = postgres_connection.cursor()


# create the standings table
create_table_sql_query = """
    DROP TABLE IF EXISTS standings_table CASCADE;
    CREATE TABLE standings_table (
        position INT,
        logo VARCHAR(255),
        team VARCHAR(255),
        games_played INTEGER,
        wins INTEGER,
        draws INTEGER,
        losses INTEGER,
        goals_for INTEGER,
        goals_against INTEGER,
        goal_difference INTEGER,
        points INTEGER,
        league_name VARCHAR(255),
        PRIMARY KEY (position, league_name)
    );
"""


cur.execute(create_table_sql_query)
postgres_connection.commit()
logging.info("Standings table created successfully.")


# insert standings data for each league
insert_data_sql_query = """
    INSERT INTO public.standings_table (
        position, logo, team, games_played, wins, draws, losses, 
        goals_for, goals_against, goal_difference, points, league_name
    ) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (position, league_name) DO UPDATE SET
        logo = EXCLUDED.logo,
        team = EXCLUDED.team,
        games_played = EXCLUDED.games_played,
        wins = EXCLUDED.wins,
        draws = EXCLUDED.draws,
        losses = EXCLUDED.losses,
        goals_for = EXCLUDED.goals_for,
        goals_against = EXCLUDED.goals_against,
        goal_difference = EXCLUDED.goal_difference,
        points = EXCLUDED.points;
"""


# fetch data for each league
for league_id, league_name in leagues.items():
    try:
        logging.info(f"Fetching data for {league_name} (League ID: {league_id})...")
        db_config, standings_data = api_handler.get_api_response(league_id)

        # extract standings information
        standings = standings_data[0]['league']['standings'][0]

        # prepare data for insertion
        data_list = []
        for team_info in standings:
            data_list.append([
                team_info['rank'],
                team_info['team']['logo'],
                team_info['team']['name'],
                team_info['all']['played'],
                team_info['all']['win'],
                team_info['all']['draw'],
                team_info['all']['lose'],
                team_info['all']['goals']['for'],
                team_info['all']['goals']['against'],
                team_info['goalsDiff'],
                team_info['points'],
                league_name,
            ])

        # insert data into the database
        for row in data_list:
            cur.execute(insert_data_sql_query, row)

        postgres_connection.commit()
        logging.info(f"Data for {league_name} inserted successfully.")
    except Exception as e:
        logging.error(f"Error processing data for {league_name}: {e}")



# create a ranked view for all leagues
create_ranked_standings_view_sql_query= """
    CREATE OR REPLACE VIEW public.standings_table_vw AS 
        SELECT 
            league_name,
            RANK() OVER (PARTITION BY league_name ORDER BY points DESC, goal_difference DESC, goals_for DESC) AS position,
            logo,
            team,
            games_played,
            wins,
            draws,
            losses,
            goals_for,
            goals_against,
            goal_difference,
            points
        FROM public.standings_table;
"""



cur.execute(create_ranked_standings_view_sql_query)
postgres_connection.commit()
logging.info("Ranked standings view created successfully.")


# close the database connection
cur.close()
postgres_connection.close()
logging.info("Database connection closed.")


print("Standings data for all leagues has been successfully updated!")
