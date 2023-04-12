import pandas as pd

df_news = pd.read_csv("news.csv")
df_urls = pd.read_csv("urls.csv")

print("\nThe length of df_news is:", len(df_news))
print("The length of df_urls is:", len(df_urls), "\n")