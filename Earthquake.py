# ============================================================
# IMPORTING REQUIRED LIBRARIES
# ============================================================

print("Program started")
import pandas as pd
import requests
from datetime import datetime

# ============================================================
# SETTING THE DATE RANGE
# Fetch earthquake data for the last 5 years up to the
# current year.
# ============================================================

start_year = datetime.now().year - 5
end_year = datetime.now().year

# List used to store earthquake records from the API
all_records = []

# ============================================================
# FETCHING EARTHQUAKE DATA FROM USGS API
# ============================================================

for year in range(start_year, end_year + 1): # Loop through each year
    for month in range(1, 13): # Loop through each month

        start_date = f"{year}-{month:02d}-01"

        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"

        url = "https://earthquake.usgs.gov/fdsnws/event/1/query" # USGS Earthquake API URL
         # Parameters sent to the USGS API
        params = {
            "format": "geojson",
            "starttime": start_date,
            "endtime": end_date,
            "minmagnitude": 3
        }

        response = requests.get(url, params=params)   # Send request to the USGS API
        if response.status_code != 200:
            print(f"Request failed for {start_date}: {response.status_code}")
            continue
        data = response.json()

        # ===========================
        # EXTRACTING REQUIRED FIELDS 
        # ===========================
        for feature in data["features"]:
            all_records.append({
                "id": feature["id"],
                "time":feature["properties"]["time"],
                "updated":feature["properties"]["updated"],
                "latitude":feature["geometry"]["coordinates"][1],
                "longitude":feature["geometry"]["coordinates"][0],
                "depth_km":feature["geometry"]["coordinates"][2],
                "mag":feature["properties"]["mag"],
                "magType":feature["properties"]["magType"],
                "place":feature["properties"]["place"],
                "status":feature["properties"]["status"],
                "tsunami":feature["properties"]["tsunami"],
                "alert":feature["properties"]["alert"],
                "felt":feature["properties"]["felt"],
                "cdi":feature["properties"]["cdi"],
                "mmi":feature["properties"]["mmi"],
                "sig":feature["properties"]["sig"],
                "net":feature["properties"]["net"], 
                "code":feature["properties"]["code"],
                "ids":feature["properties"]["ids"],
                "sources":feature["properties"]["sources"],
                "types":feature["properties"]["types"],
                "nst":feature["properties"]["nst"], 
                "dmin":feature["properties"]["dmin"],
                "rms":feature["properties"]["rms"],
                "gap":feature["properties"]["gap"],
                "type":feature["properties"]["type"]
            })
# ============================================================
# CONVERTING API DATA INTO A PANDAS DATAFRAME
# ============================================================
data = pd.DataFrame(all_records)

# ============================================================
# INITIAL DATA EXPLORATION
# ============================================================
print(data.head())
print("Total records:", len(data))
print(data.shape)
print(data.columns)
print(data.dtypes)
print(data.info())
print(data.describe())
print(data.isnull().sum())
print(data["id"].duplicated().sum())
print(data.isnull().mean())

# ===================================================================
# DATA CLEANING AND DERIVING ADDITIONAL COLUMNS REQUIRED FOR ANALYSIS
# ===================================================================

data.columns = data.columns.str.strip()
data["time"] = pd.to_datetime(data["time"],unit="ms")
data["updated"] = pd.to_datetime(data["updated"],unit="ms")
data["country"] = data["place"].str.split(",").str[-1].astype(str)
data["alert"] = data["alert"].str.lower()
data["year"] = data["time"].dt.year
data["month"] = data["time"].dt.month
data["day"] = data["time"].dt.day_name()
data["day_of_week"] = data["time"].dt.day_of_week
data["hour"] = data["time"].dt.hour
data["depth_flag"] = ["Shallow" if x < 70 else "Deep" if x > 300 else "None" for x in data["depth_km"]]
data["mag_flag"] = ["Destructive" if x >= 7 else "Strong" if x >= 6 else "Normal" for x in data["mag"]]
data.select_dtypes(include="number").isnull().sum() # Check missing values for numerical column
data.select_dtypes(exclude="number").isnull().sum() # Check missing values for categorical column
data["alert"] = data["alert"].fillna("none") # Fill missing alert values with none
num_cols = data.select_dtypes(include="number").columns
missing_percent = data[num_cols].isnull().mean() * 100 # Check missing values as percentage
filtered_cols = missing_percent[missing_percent < 40].index
for col in filtered_cols:
    median_value = data[col].median()
    data[col] = data[col].fillna(median_value)

data["felt"] = data["felt"].fillna(0)

print(data.columns)
print(data.isnull().mean())


# ============================================================
# CONNECTING PYTHON WITH MYSQL
# ============================================================

from sqlalchemy import create_engine
import pymysql
#Creating a database engine
engine = create_engine("mysql+pymysql://root:Symbiance@localhost:3306/earthquake_db")

# ============================================================
# PUSHING DATA INTO MYSQL
# ============================================================
data.to_sql("earthquakes", engine, if_exists="replace", index=False)

# ============================================================
# READING SQL TABLE INTO PYTHON
# ============================================================

data = pd.read_sql("SELECT * FROM earthquakes", con=engine)
