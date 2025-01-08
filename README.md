# Football Soccer Data Pipeline

## Overview
The **Football Soccer Data Pipeline** is a Python-based project that fetches real-time football league standings using the [API-SPORTS](https://www.api-football.com/) API, stores the data in a PostgreSQL database, and visualizes it through an interactive **Streamlit** web application. This project allows users to view and analyze standings, goals, wins, and other performance metrics for various top football leagues.

## Features

- Fetches real-time football standings data from API-SPORTS.
- Stores league data in a PostgreSQL database for further analysis.
- Visualizes standings and team statistics using an interactive Streamlit dashboard.
- Supports multiple leagues, including:
  - Premier League
  - La Liga
  - Serie A
  - Bundesliga
  - Ligue 1
- Provides downloadable standings in CSV format.
- Interactive visualizations include:
  - Bar charts for points standings.
  - Stacked bar charts for wins, draws, and losses.
  - Grouped bar charts for goals scored vs. goals conceded.

## Requirements

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 13 or higher
- API key from [API-SPORTS](https://www.api-football.com/)

### Python Packages
Install required Python packages using `pip`:
```bash
pip install -r requirements.txt
```

### Tools Used
- **API-Sports**: For fetching real-time football data.
- **PostgreSQL**: Database to store league standings.
- **Streamlit**: For creating an interactive web application.
- **Plotly**: For creating advanced visualizations.
- **dotenv**: To securely manage environment variables.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/ericseppanen999/football-data-pipeline.git
cd football-data-pipeline
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory and add the following:
```env
API_KEY=your_api_key
API_HOST=v3.football.api-sports.io
SEASON=2023
DB_NAME=football_data
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 3. Set Up the PostgreSQL Database
1. Create a PostgreSQL database:
   ```sql
   CREATE DATABASE football_data;
   ```
2. Run the database handler script to create tables and populate data:
   ```bash
   python database_handler.py
   ```

### 4. Launch the Streamlit App
Run the Streamlit application:
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

## Project Structure
```
football-data-pipeline/
├── app.py                # Streamlit dashboard for visualizing data
├── database_handler.py   # Handles database setup and data population
├── api_handler_01.py     # API handler for fetching league standings
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (ignored in Git)
├── README.md             # Project documentation
└── assets/               # League logos
```

## Usage
1. Select a league from the sidebar.
2. View the standings, points, and match statistics.
3. Interact with visualizations to analyze team performance.
4. Download the standings as a CSV file if needed.

## Visualizations
- **Points Standings**: Bar chart ranking teams by points.
- **Match Outcomes**: Stacked bar chart of wins, draws, and losses.
- **Goals Analysis**: Grouped bar chart comparing goals scored vs. goals conceded.

## Future Enhancements
- Add player-level statistics for more detailed analysis.
- Incorporate predictive analytics for league outcomes.
- Enhance the app with advanced filtering options.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Open a pull request.

## License
This project is licensed under the MIT License. See `LICENSE` for details.

## Acknowledgements
- [API-SPORTS](https://www.api-football.com/) for providing the football data.
- [Streamlit](https://streamlit.io/) for the interactive dashboard framework.
- [Plotly](https://plotly.com/) for advanced data visualizations.
