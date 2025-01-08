import os
import psycopg2
import pandas as pd
from PIL import Image
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
import plotly.graph_objects as go
import io
import logging

logging.basicConfig(
    filename="application.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_HOST = os.getenv("API_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


# define the leagues to fetch (league_name: league_id)
leagues = {
    "Premier League":39,
    "La Liga":140,
    "Serie A":135,
    "Bundesliga":78,
    "Ligue 1":61
}


# connect to postgres
def get_postgres_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )



# fetch the league standings from the database
def get_league_standings(league_name):
    query = f"""
        SELECT 
            position,
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
        FROM public.standings_table_vw
        WHERE league_name = %s
        ORDER BY position;
    """
    with get_postgres_connection() as conn:
        return pd.read_sql(query, conn, params=(league_name,))



# convert df to csv
def convert_df_to_csv(df):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()



# configure page
st.set_page_config(
    page_title="Football League Standings",
    layout="wide"
)



# sidebar league selector
st.sidebar.title("Select a League")
selected_league = st.sidebar.selectbox(
    "Choose a league to display:",
    options=["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
)
logging.info(f"User selected {selected_league} from the sidebar.")


if selected_league:
    # open league image
    league_val=leagues[selected_league]
    league_logo_filepath=f"assets/{league_val}.png"
    league_logo=Image.open(league_logo_filepath)

    col1,col2=st.columns([4,1])
    col2.image(league_logo)

    # fetch league standings
    final_standings_df=get_league_standings(selected_league)
    logging.info(f"Standings fetched successfully for {selected_league}.")
    
    # update the logo column to display images
    final_standings_df["logo_img"]=final_standings_df["logo"].apply(lambda url: f"<img src='{url}' width='40'>")

    # df for display
    display_df=final_standings_df[[
        "position", "logo_img", "team", "games_played", "wins", "draws", "losses",
        "goals_for", "goals_against", "goal_difference", "points"
    ]].copy()

    # display the dataframe as a table
    html_table=display_df.to_html(
        escape=False,
        index=False,
        justify="left"
    )


    # title
    st.markdown(f"## {selected_league} Standings for the 2023/24 season:")

    # actual table
    st.markdown(html_table, unsafe_allow_html=True)



    # plotly bar chart
    fig=px.bar(
        final_standings_df,
        x="team",
        y="points",
        title=f"{selected_league} Standings",
        labels={
            "points":"Points",
            "team":"Team",
            "goals_for":"Goals Scored",
            "goals_against":"Goals Conceded",
            "goal_difference":"Goal Difference"
        },
        color="team",
        height=700,
        hover_data=["goals_for","goals_against","goal_difference"]
    )
    st.plotly_chart(fig,use_container_width=True)



    # bar chart for w/d/l
    fig_stacked_bar=px.bar(
        final_standings_df,
        x="team",
        y=["wins", "draws", "losses"],
        title=f"{selected_league}:Match Outcomes per Team",
        labels={"value":"Number of Matches",
                 "variable":"Outcome"
        },
        barmode="stack",
        height=500
        )
    st.plotly_chart(fig_stacked_bar,use_container_width=True)



    # grouped bar chart for goals scored vs. goals conceded
    fig_grouped_bar=px.bar(
    final_standings_df,
    x="team",
    y=["goals_for","goals_against"],
    title=f"{selected_league}: Goals Scored vs. Goals Conceded",
    labels={"value":"Goals","variable":"Metric"},
    barmode="group",
    height=500
    )
    st.plotly_chart(fig_grouped_bar,use_container_width=True)
    


    # download as CSV
    csv_data = convert_df_to_csv(final_standings_df)
    st.sidebar.download_button(
        label=f"📥 Download {selected_league} Standings as CSV",
        data=csv_data,
        file_name=f"{selected_league}_standings.csv",
        mime="text/csv"
    )

