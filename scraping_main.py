# From data scraping to generating a analysis-ready datasets
import pandas as pd
from datetime import datetime
from urls_scraping import urls_scraping
from news_scraping import news_scraping
from preprocessing import preprocessing
from sentiment_analysis import sentiment_analysis


# Configurations
today = datetime.today().strftime("%m/%d/%Y")
keyword = "(mask mandate OR wear mask OR mask rule) AND covid"
with open("log.txt", "r") as f:
    from_date = f.readline().strip()
    if from_date == "":
        from_date = today
to_date = today

# 1: URLs scraping
urls_scraping(keyword=keyword, from_date=from_date, to_date=to_date)

# 2: News scraping
news_scraping()

# 3: Data preprocessing
df = pd.read_csv("news.csv")
df = preprocessing(df)

# 4: Sentiment analysis
df = sentiment_analysis(df)

# 5: Save the data as a csv file
df.to_csv("analysis_ready.csv", index=False)
print("The data is ready for analysis!\n")
