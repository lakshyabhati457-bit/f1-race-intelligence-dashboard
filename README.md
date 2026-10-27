# Formula 1 Race Intelligence Dashboard Analysis Report (2010–2026)

An interactive Formula 1 analysis dashboard built with **Python, Streamlit, Pandas and Plotly**, with a data model suitable for Tableau worksheets and dashboards.

## Dashboard modules
- Driver points leaderboard
- Constructor points by season
- Podium distribution by driver and team
- Grand Prix events by host country/circuit
- Retirement/status patterns and team-level retirement-rate proxy
- Filters for season, constructor and driver
- Data notes that distinguish supported metrics from fields requiring additional sources

## Quick start
Requires Python 3.10+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python download_data.py
streamlit run app.py
```

The app opens locally in your browser. The `data/` directory is intentionally git-ignored to avoid committing a large third-party dataset; the downloader retrieves the public archive when run.

## Data source
Dataset archive: [TracingInsights/RaceData](https://github.com/TracingInsights/RaceData)  
Archive URL: https://github.com/TracingInsights/RaceData/releases/latest/download/data.zip

Review the upstream repository and its licensing/attribution terms before redistributing data. Do not describe this project as an official Formula 1 product.

## Tableau build
The CSV files can also be connected in Tableau Desktop/Public:
1. Connect to `races.csv` and join `results.csv` on `raceId`.
2. Join `drivers.csv` on `driverId`, `constructors.csv` on `constructorId`, `circuits.csv` on `circuitId`, and `status.csv` on `statusId`.
3. Filter `year` to 2010–2026.
4. Build sheets for driver points, constructor points by season, podiums, host country participation, and result status.
5. Assemble a dashboard and add season/team filters.
6. Publish through Tableau Public and copy the public workbook URL into your project submission.

## Publish the interactive demo
### Streamlit Community Cloud
1. Push this repository to your GitHub account.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Deploy this repository, selecting `app.py` as the main file.
4. The app will download the dataset on first run. If outbound downloads are blocked, commit the required CSVs only after confirming their licence permits redistribution, or modify the app to use an approved hosted data source.
5. Copy the public app URL to your project workspace.

## GitHub repository
Create a new public repository named `f1-race-intelligence-dashboard`, upload these files, and paste its URL into the **Add Github Link** field. Do not paste the source dataset's repository as if it were your own project.

## Important analytical limitations
- The 2026 season is in progress and will be incomplete.
- Historical points systems changed, so cross-era point totals are not perfectly comparable without normalization.
- The provided result-status field supports a retirement/status analysis, but not a reliable engine/brake/collision failure taxonomy.
- Tyre compound strategy (Soft/Medium/Hard/Intermediate) is not included in this starter dashboard unless compound-level data is available in a validated source. Do not infer tyre compounds from finish positions.
- The project description mentions 6,464 records; verify this against the downloaded data and the exact table/grain before using it as a factual total.

## Suggested submission metadata
**Project:** Formula 1 Race Intelligence Dashboard Analysis Report (2010–2026)  
**Type:** Individual  
**Skills:** Data preprocessing, data visualization, dashboard design, Tableau, Python  
**Status:** Dashboard source prepared; publish demo and GitHub links after deployment.
