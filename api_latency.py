import requests
import time
import pandas as pd
import statistics as stats
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
from PIL import Image
from scipy.stats import ttest_1samp
# Define the API endpoints
apis = {
    "News API": "https://newsapi.org/v2/everything?q=tesla&from=2023-03-18&sortBy=publishedAt&apiKey=YOUR_API_KEY",
    "OpenWeatherMap API": "https://api.openweathermap.org/data/3.0/onecall?lat={33.4255}&lon={111.9400}&appid={YOUR_API_KEY}",
    "Alpha Advantage API": "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&outputsize=full&apikey=demo",
    "Pixabay API": "https://pixabay.com/api/?key=YOUR_API_KEY",
    "IP API": "http://ip-api.com/json/68.3.173.11",
    "NASA API": "https://api.nasa.gov/insight_weather/?api_key=YOUR_API_KEY&feedtype=json&ver=1.0",
    "FDA API": "https://api.fda.gov/drug/event.json?limit=1",
    "Earthquake API": "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2020-01-01&endtime=2020-01-02",
    "World Health Organization API": "https://covid19.who.int/WHO-COVID-19-global-data.csv",
    "OpenCage API":"https://api.opencagedata.com/geocode/v1/json?key=YOUR_API_KEY%2C+9.7334394&pretty=1&no_annotations=1",
    "ISS Locator API": "http://api.open-notify.org/iss-now.json",
    "Github API": "https://api.github.com/users/openai/repos",
    "National Park Service API": "https://developer.nps.gov/api/v1/parks?parkCode=acad&api_key=DEMO_KEY",
    "Google Books API": "https://www.googleapis.com/books/v1/volumes?q=isbn:0747532699",
    "Open Library API": "https://openlibrary.org/books/OL7353617M.json",
    "COVID-19 API": "https://corona.lmao.ninja/v3/covid-19/countries",
    "National Library of Medicine":"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=science[journal]+AND+breast+cancer+AND+2008[pdat]/",
    "National Oceanic and Atmospheric Administration API": "https://www.ncdc.noaa.gov/cdo-web/api/v2/datasets",
    "National Highway Traffic Safety Administration API": "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeId/440?format=json",
    "Open Air Quality API" : "https://api.openaq.org/v2/sources",
    "New York Times API": "https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key=YOUR_API_KEY",
    "Instagram API": "https://www.instagram.com/instagram/?__a=1",
    "Map Quest API": "https://www.mapquestapi.com/datamanager/v2/get-column-types?key=YOUR_API_KEY",
    "REST couintries API": "https://restcountries.com/v3.1/all",
    "World Bank API": "https://api.worldbank.org/v2/country?format=json", 
}

# Initialize an empty dictionary to store latencies
latencies = {}


MAX_BYTES = 64   # Maximum number of bytes to download from each API

excel_file = "api_latency.xlsx"
# Make API calls and measure the latency
for name, url in apis.items():
    start_time = time.time()
    response = requests.get(url,stream=True)
    data = response.raw.read(MAX_BYTES)
    end_time = time.time()

    latency = (end_time - start_time) * 1000  # Convert to milliseconds
    latencies[name] = latency
    print(f"Latency for {name}: {latency:.2f} ms")

# add the data to a dataframe
df = pd.DataFrame.from_dict(latencies, orient="index", columns=["Latency (ms)"])
df["API"] = df.index



#calculate sample mean & sample standard deviation
latency_values = list(latencies.values())

sample_mean = np.mean(latency_values)
sample_std = np.std(latency_values, ddof=1)

#do t test 
# Null hypothesis: mean loading times are >= 500 ms
# Alternative hypothesis: mean loading times are < 500 ms
mu0 = 500
alpha = 0.05
t_stat, p_val = ttest_1samp(latency_values, mu0, alternative='less')

#add these to the dataframe
df["Sample Mean"] = sample_mean
df["Sample Standard Deviation"] = sample_std
df["t-statistic"] = t_stat
df["p-value"] = p_val
df["Null Hypothesis"] = "mean loading times are >= 500 ms"
df["Alternative Hypothesis"] = "mean loading times are < 500 ms"

if p_val < alpha:
    df["Conclusion"] = "Reject null hypothesis: mean loading times are less than 500 ms"
else:
    df["Conclusion"] = "Fail to reject null hypothesis: mean loading times are greater than or equal to 500 ms"
    
#reorder columns
df = df[["API", "Latency (ms)", "Sample Mean", "Sample Standard Deviation","t-statistic", "p-value","Conclusion", "Null Hypothesis", "Alternative Hypothesis"]]

#create excel file
df.to_excel(excel_file, index =False)

# Create the histogram
n, bins, patches = plt.hist(latencies.values(), bins=5)

# Add axis labels and title
plt.xlabel("Latency (ms)")
plt.ylabel("Frequency")
plt.title("API Latency Histogram")

# Label each bin with its frequency
for i in range(len(patches)):
    plt.text(x=bins[i]+(bins[i+1]-bins[i])/2, y=n[i], s=int(n[i]), ha='center', va='bottom')

# Save the figure
plt.savefig("histogram_latency.png")

# Add the histogram to the excel file
worksheet = pd.read_excel(excel_file)
worksheet.insert(loc=4, column="Histogram", value="")
worksheet.to_excel(excel_file, index=False)

workbook = openpyxl.load_workbook(excel_file)
worksheet = workbook.active
img = openpyxl.drawing.image.Image("histogram_latency.png")
worksheet.add_image(img, "E2")
workbook.save(excel_file)