import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="F1 Race Intelligence | 2010–2026", page_icon="🏎️", layout="wide")
DATA = Path("data")

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem}
h1 {letter-spacing: -0.04em}
[data-testid="stMetric"] {background:#141820; border:1px solid #2b303a; padding:14px 16px; border-radius:12px}
</style>
""", unsafe_allow_html=True)

st.title("🏎️ Formula 1 Race Intelligence")
st.caption("Interactive race analysis • 2010–2026 • Tableau-ready data model")

@st.cache_data
def load_csv(name):
    p = DATA / name
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, na_values=["\\N", "\\\\N"])

results = load_csv("results.csv")
races = load_csv("races.csv")
drivers = load_csv("drivers.csv")
constructors = load_csv("constructors.csv")
circuits = load_csv("circuits.csv")
status = load_csv("status.csv")

required = {"results.csv": results, "races.csv": races, "drivers.csv": drivers, "constructors.csv": constructors}
missing = [n for n, df in required.items() if df.empty]
if missing:
    st.warning("Dataset not found yet. Run `python download_data.py` as described in README.md, then refresh this page.")
    st.markdown("The project uses the public Formula 1 CSV archive from [TracingInsights/RaceData](https://github.com/TracingInsights/RaceData).")
    st.stop()

for df in [results, races, drivers, constructors, circuits, status]:
    if not df.empty:
        for c in df.columns:
            if c in {"year", "round", "raceId", "driverId", "constructorId", "statusId", "points", "positionOrder", "grid", "laps"}:
                df[c] = pd.to_numeric(df[c], errors="coerce")

races = races[(races["year"] >= 2010) & (races["year"] <= 2026)].copy()
results = results[results["raceId"].isin(races["raceId"])].copy()
df = results.merge(races[["raceId","year","round","name","circuitId","date"]], on="raceId", how="left", suffixes=("","_race"))
df = df.merge(drivers[["driverId","forename","surname","nationality"]], on="driverId", how="left")
df["Driver"] = (df["forename"].fillna("") + " " + df["surname"].fillna("")).str.strip()
df = df.merge(constructors[["constructorId","name"]].rename(columns={"name":"Team"}), on="constructorId", how="left")
if not circuits.empty:
    # Dataset releases vary in circuit name column: commonly `name`, sometimes `circuitName`.
    circuit_name_col = "circuitName" if "circuitName" in circuits.columns else ("name" if "name" in circuits.columns else None)
    circuit_cols = ["circuitId"]
    if "country" in circuits.columns:
        circuit_cols.append("country")
    if circuit_name_col:
        circuit_cols.append(circuit_name_col)
    circuit_lookup = circuits[circuit_cols].copy()
    if circuit_name_col and circuit_name_col != "circuitName":
        circuit_lookup = circuit_lookup.rename(columns={circuit_name_col: "circuitName"})
    if "country" not in circuit_lookup.columns:
        circuit_lookup["country"] = "Unknown"
    if "circuitName" not in circuit_lookup.columns:
        circuit_lookup["circuitName"] = "Unknown circuit"
    df = df.merge(circuit_lookup[["circuitId","country","circuitName"]], on="circuitId", how="left")
else:
    df["country"] = "Unknown"
    df["circuitName"] = "Unknown circuit"
if not status.empty and "statusId" in df.columns:
    df = df.merge(status[["statusId","status"]], on="statusId", how="left")
else:
    df["status"] = ""
df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0)
df["positionOrder"] = pd.to_numeric(df["positionOrder"], errors="coerce")
df["Podium"] = df["positionOrder"].between(1,3)
df["Finished"] = df["status"].fillna("").str.lower().eq("finished") | df["status"].fillna("").str.contains(r"\+\s*\d+\s*lap", case=False, regex=True)
df["Retired"] = ~df["Finished"] & ~df["status"].fillna("").str.lower().isin(["disqualified","excluded","did not qualify","did not prequalify","withdrawn"])

years = sorted(df["year"].dropna().astype(int).unique())
teams = sorted(df["Team"].dropna().unique())
c1,c2,c3 = st.columns([1,1,2])
with c1:
    yr = st.selectbox("Season", ["All seasons"] + years[::-1], index=0)
with c2:
    team = st.selectbox("Constructor", ["All constructors"] + teams)
with c3:
    driver_search = st.text_input("Find a driver", placeholder="e.g. Verstappen, Hamilton")

f = df.copy()
if yr != "All seasons":
    f = f[f["year"] == int(yr)]
if team != "All constructors":
    f = f[f["Team"] == team]
if driver_search.strip():
    f = f[f["Driver"].str.contains(driver_search.strip(), case=False, na=False)]

m1,m2,m3,m4 = st.columns(4)
m1.metric("Race entries", f"{len(f):,}")
m2.metric("Drivers", f["Driver"].nunique())
m3.metric("Constructors", f["Team"].nunique())
m4.metric("Podium finishes", f"{int(f['Podium'].sum()):,}")

tab1,tab2,tab3,tab4,tab5 = st.tabs(["🏆 Driver leaderboard","📈 Constructors","🥇 Podiums","🌍 Circuits & countries","🛠️ Reliability / DNF"])
with tab1:
    st.subheader("Cumulative points by driver")
    dpoints = f.groupby("Driver", as_index=False)["points"].sum().sort_values("points", ascending=False).head(20)
    if not dpoints.empty:
        st.plotly_chart(px.bar(dpoints.sort_values("points"), x="points", y="Driver", orientation="h",
            title="Top 20 drivers by points in selected scope", labels={"points":"Points","Driver":"Driver"},
            color="points", color_continuous_scale="reds"), use_container_width=True)
    st.dataframe(dpoints.sort_values("points", ascending=False), use_container_width=True, hide_index=True)
with tab2:
    st.subheader("Constructor points by season")
    cp = df.groupby(["year","Team"], as_index=False)["points"].sum()
    if team != "All constructors": cp = cp[cp["Team"] == team]
    topteams = cp.groupby("Team")["points"].sum().nlargest(8).index
    cp = cp[cp["Team"].isin(topteams)]
    if not cp.empty:
        st.plotly_chart(px.line(cp, x="year", y="points", color="Team", markers=True,
            title="Season-by-season constructor points"), use_container_width=True)
with tab3:
    st.subheader("Podium distribution")
    pods = f[f["Podium"]].groupby(["Driver","Team"], as_index=False).size().rename(columns={"size":"Podiums"})
    pods = pods.sort_values("Podiums", ascending=False).head(25)
    if not pods.empty:
        st.plotly_chart(px.bar(pods.sort_values("Podiums"), x="Podiums", y="Driver", color="Team",
            orientation="h", title="Top podium achievers"), use_container_width=True)
    st.caption("Podiums are defined as classified finishing positions 1–3.")
with tab4:
    st.subheader("Grand Prix participation by host country")
    if "country" in f.columns:
        country_races = f[["raceId","country","name"]].drop_duplicates().groupby("country", as_index=False).size().rename(columns={"size":"Grand Prix events"})
        country_races = country_races.sort_values("Grand Prix events", ascending=False).head(20)
        st.plotly_chart(px.bar(country_races.sort_values("Grand Prix events"), x="Grand Prix events", y="country",
            orientation="h", title="Countries hosting the most events in selected scope"), use_container_width=True)
    st.dataframe(f[["year","name","country","circuitName"]].drop_duplicates().sort_values(["year","name"]), use_container_width=True, hide_index=True)
with tab5:
    st.subheader("Retirement / reliability analysis")
    rel = f.groupby(["Team","status"], as_index=False).size().rename(columns={"size":"Entries"})
    rel = rel[~rel["status"].fillna("").str.lower().isin(["finished"])].sort_values("Entries", ascending=False).head(30)
    if not rel.empty:
        st.plotly_chart(px.bar(rel, x="Entries", y="status", color="Team", orientation="h",
            title="Most frequent recorded result statuses (top 30 team/status combinations)"), use_container_width=True)
    dnf = f.groupby("Team", as_index=False).agg(Entries=("resultId","count"), Retirements=("Retired","sum"))
    dnf["Retirement rate (%)"] = (dnf["Retirements"] / dnf["Entries"] * 100).round(1)
    st.dataframe(dnf.sort_values("Retirement rate (%)", ascending=False), use_container_width=True, hide_index=True)
    st.caption("This is a status-based proxy, not a definitive mechanical-failure classification. Specific causes need a normalized failure taxonomy.")

with st.expander("Data notes & limitations"):
    st.write("""
    - The dashboard filters race results to seasons 2010–2026. The 2026 season is partial as of the latest dataset release.
    - Points reflect the points recorded in the source results table; historical scoring systems differ by era.
    - Tyre-compound analysis requires a tyre strategy/pit-stop dataset with compound labels. This starter app does not fabricate tyre compounds where the source table lacks them.
    - DNF/reliability is based on recorded result status and should not be interpreted as engine/brake/collision failure attribution without validated cause labels.
    - Data source: TracingInsights/RaceData, which republishes Formula 1 datasets. See source repository and data licensing before redistribution.
    """)
st.divider()
st.caption("Formula 1 Race Intelligence Dashboard • Built with Streamlit + Plotly • For academic analysis")
