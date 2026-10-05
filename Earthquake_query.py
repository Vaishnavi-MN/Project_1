# ============================================================
# CONNECTING PYTHON WITH MYSQL
# ============================================================
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import streamlit as st
#Creating a database engine
engine = create_engine("mysql+pymysql://root:Symbiance@localhost:3306/earthquake_db")


# ============================================================
# READING SQL TABLE INTO PYTHON
# ============================================================

data = pd.read_sql("SELECT * FROM earthquakes", con=engine)

# ============================================================
# SQL QUERIES FOR EARTHQUAKE ANALYSIS
# ============================================================

queries = {
    "1.Top 10 strongest earthquakes (mag)" : 
    """SELECT * FROM earthquakes
    WHERE type = "earthquake"
    ORDER BY mag desc
    LIMIT 10;""",

    "2.Top 10 deepest earthquakes (depth_km)" : 
    """SELECT * FROM earthquakes
    WHERE type = "earthquake" 
    ORDER BY depth_km desc
    LIMIT 10;""",

    "3.Shallow earthquakes < 50 km and mag > 7.5" : 
    """SELECT * FROM earthquakes
    WHERE depth_km < 50 and mag > 7.5 
    and type = "earthquake";""",

    "5.Average magnitude per magnitude type (magType)" : 
    """SELECT magType, avg(mag) as avg_mag 
    FROM earthquakes
    GROUP BY magType;""",

    "6.Year with most earthquakes" : 
    """SELECT year, count(*) as count_of_eq FROM earthquakes
    WHERE type = "earthquake" 
    GROUP BY year
    ORDER BY count_of_eq DESC
    LIMIT 1;""",

    "7.Month with highest number of earthquakes" : 
    """SELECT month, count(*) as count_of_eq 
    FROM earthquakes
    WHERE type = "earthquake" 
    GROUP BY month
    ORDER BY count_of_eq DESC
    LIMIT 1;""",

    "8.Day of week with most earthquakes" : 
    """SELECT day_of_week, count(*) as count_of_eq 
    FROM earthquakes
    WHERE type = "earthquake" 
    GROUP BY day_of_week
    ORDER BY count_of_eq DESC
    LIMIT 1;""",

    "9.Count of earthquakes per hour of day" : 
    """SELECT hour, count(*) as count_of_eq 
    FROM earthquakes
    WHERE type = "earthquake" 
    GROUP BY hour
    ORDER BY hour;""",

    "10.Most active reporting network (net)" : 
    """SELECT net, count(*) as count_of_network
    FROM earthquakes
    GROUP BY net
    ORDER BY count_of_network DESC
    LIMIT 1;""",

    "11.Top 5 places with highest casualties" : 
    """SELECT place, MAX(felt) as felt_reports
    FROM earthquakes
    GROUP BY place
    ORDER BY felt_reports DESC
    LIMIT 5;""",

    "13.Count of earthquakes by alert level" : 
    """SELECT alert, count(*) as total
    FROM earthquakes
    WHERE alert != "none"
    GROUP BY alert;""",

    "14.Count of reviewed vs automatic earthquakes (status)" : 
    """SELECT status, count(*) as total
    FROM earthquakes
    GROUP BY status;""",

    "15.Count by earthquake type (type)" : 
    """SELECT type, count(*) as total
    FROM earthquakes
    GROUP BY type;""",

    "16.Number of earthquakes by data type (types)" : 
    """SELECT types, count(*) as total
    FROM earthquakes
    GROUP BY types;""",

    "18.Events with high station coverage (nst > threshold)" : 
    """SELECT * FROM earthquakes
    WHERE nst > 100
    ORDER BY nst desc;""",

    "19.Number of tsunamis triggered per year" : 
    """SELECT year, COUNT(tsunami) as tsunami_triggered
    FROM earthquakes
    WHERE tsunami = 1
    GROUP BY year;""",

    "20.Count earthquakes by alert levels (red, orange, etc.)" :
     """SELECT alert, count(*) as earthquakes
    FROM earthquakes
    WHERE type = "earthquake"
    GROUP BY alert;""",

    "21.Top 5 countries with the highest average magnitude of earthquakes in the past 5 years" : 
    """SELECT country, AVG(mag) as average_mag
    FROM earthquakes
    WHERE type = "earthquake"
    GROUP BY country
    ORDER BY average_mag DESC
    LIMIT 5;""",

    "22.Countries that have experienced both shallow and deep earthquakes within the same month" : 
    """SELECT country,year,month
    FROM earthquakes
    GROUP BY country,year, month
    HAVING MIN(depth_km) < 70 and MAX(depth_km) > 300;""",

    "23.year-over-year growth rate in the total number of earthquakes globally" : 
    """SELECT year,earthquake_count,
        ROUND(
            (earthquake_count - LAG(earthquake_count) OVER (ORDER BY year))
            * 100.0
            / LAG(earthquake_count) OVER (ORDER BY year),
            2
        ) AS yoy_growth_rate
    FROM (
        SELECT year,COUNT(*) AS earthquake_count
        FROM earthquakes
        WHERE type = "earthquake"
        GROUP BY year
    ) AS yearly_counts
    ORDER BY year;""",

   "24.The 3 most seismically active regions by combining both frequency and average magnitude" :
   """SELECT
        place,
        COUNT(*) AS frequency,
        ROUND(AVG(mag), 2) AS average_magnitude,
        ROUND(COUNT(*) * AVG(mag), 2) AS activity_score
    FROM earthquakes
    GROUP BY place
    ORDER BY activity_score DESC
    LIMIT 3;""",

    "25.The average depth of earthquakes within ±5° latitude range of the equator" :
    """SELECT country, AVG(depth_km) as average_depthkm
    FROM earthquakes
    WHERE latitude BETWEEN -5 AND 5
    GROUP BY country;""",

    "26.Countries having the highest ratio of shallow to deep earthquakes" :
    """SELECT
    s.country,
    s.shallow_count,
    d.deep_count,
    ROUND(s.shallow_count / NULLIF(d.deep_count, 0), 2) AS ratio
    FROM
    (
    SELECT country, COUNT(*) AS shallow_count
    FROM earthquakes
    WHERE depth_flag = "Shallow"
    GROUP BY country
    ) AS s
    JOIN
    (SELECT country, COUNT(*) AS deep_count
    FROM earthquakes
    WHERE depth_flag = "Deep"
    GROUP BY country
    ) AS d
    ON s.country = d.country
    ORDER BY ratio DESC
    LIMIT 10;""",

    "27.The average magnitude difference between earthquakes with tsunami alerts and those without":
    """SELECT (SELECT AVG(mag) FROM earthquakes WHERE tsunami = 1) - 
    (SELECT AVG(mag) FROM earthquakes WHERE tsunami = 0)
    as avg_mag_difference;""",

    "28.Lowest data reliability using gap and rms(highest average error margins).":
    """SELECT gap, rms FROM earthquakes
    ORDER BY gap DESC, rms DESC
    LIMIT 5;""",

    "30.The regions with the highest frequency of deep-focus earthquakes (depth > 300 km)" : 
    """SELECT place, count(*) as frequency
    FROM earthquakes
    WHERE depth_km > 300
    GROUP BY place
    ORDER BY frequency DESC;""",
}


# ============================================================
# PAGE TITLE
# ============================================================

st.title("🌎 Global Seismic Trends: Data-Driven Earthquake Insights")
st.write("USGS Earthquake Data - SQL Analysis Dashboard")

# ============================================================
# SELECT QUERY
# ============================================================

selected_task = st.selectbox("Select an analysis:",list(queries.keys()))

# ============================================================
# RUN QUERY BUTTON
# ============================================================

if st.button("▶ Run Query"):

    query = queries[selected_task]

    # Display selected query
    st.subheader("SQL Query")
    st.code(query, language="sql")

    # Execute query
    result = pd.read_sql(query, con=engine)

    # Display result
    st.subheader("Query Result")
    st.dataframe(result, use_container_width=True)

# DISPLAY ALL RECORDS    
st.divider()

if st.button("Show All Earthquake Records"):
    st.subheader("🌎 All Records From Earthquake Data")
    st.dataframe(data, use_container_width=True)