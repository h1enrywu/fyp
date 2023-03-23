import re, en_core_web_sm, requests, urllib.parse
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from statistics import mode

# Step 1
def cleaning(data):
    # Remove punctuation
    data = re.sub("[^a-zA-Z]", " ", data)

    # Lowercasing
    data = data.lower()

    # Tokenize the data
    words = word_tokenize(data)

    # Remove stopwords
    stopwords_list = requests.get(
        "https://gist.githubusercontent.com/rg089/35e00abf8941d72d419224cfd5b5925d/raw/12d899b70156fd0041fa9778d657330b024b959c/stopwords.txt"
    ).content
    stopwords = set(stopwords_list.decode().splitlines())
    words = [word for word in words if not word in stopwords]

    # Lemmatization
    lem = WordNetLemmatizer()
    words = [lem.lemmatize(word) for word in words]

    # Join the words back to a string
    cleaned_data = " ".join(words)

    return cleaned_data


# Step 2
def ner(data):
    nlp = en_core_web_sm.load()
    doc = nlp(data)
    return [ent.text for ent in doc.ents if ent.label_ == "GPE"]


# Step 4
def get_region_country_dict(regions_list):
    def get_country_name(region_name):
        # encode the region name to make it URL friendly
        encoded_city_name = urllib.parse.quote(region_name)
        # make sure the output is in English
        headers = {"accept-language": "en"}
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_city_name}&format=json&limit=1"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                country_name = data[0]["display_name"].split(",")[-1].strip()
                if "Hong Kong" in data[0]["display_name"]:
                    return "Hong Kong"
                else:
                    return country_name
        return None

    region_country_dict = {}
    for region in regions_list:
        if region.isalpha() or " " in region:
            country_name = get_country_name(region)
            if country_name:
                region_country_dict[region] = country_name
            else:
                region_country_dict[region] = None
        else:
            # If data is not a valid city or country name, map it to None
            region_country_dict[region] = None
    return region_country_dict


# Step 6
def get_regions_mode(x):
    if x:
        return mode(x)
    else:
        return None


# Step 7
source_country_dict = {
    "bbc": "United Kingdom",
    "cnn": "United States",
    "thestandard": "Hong Kong",
    "rthk": "Hong Kong",
    "yomiuri": "Japan",
    "asahi": "Japan",
    "mainichi": "Japan",
    "japantimes": "Japan",
    "koreaherald": "South Korea",
    "koreatimes": "South Korea",
    "koreajoongangdaily": "South Korea",
    "hkfp": "Hong Kong",
    "theguardian": "United Kingdom",
    "dailymail": "United Kingdom",
    "foxnews": "United States",
    "news.com.au": "Australia",
    "abc": "Australia",
    "straitstimes": "Singapore",
    "todayonline": "Singapore",
}


# Main function
def preprocessing(df):
    print("Data Preprocessing the data ...")

    # 1. Cleaning
    df["Title"] = df["Title"].apply(cleaning)
    df["Content"] = df["Content"].apply(cleaning)
    df["Text"] = df["Title"] + " " + df["Content"]

    # 2. NER
    df["Regions"] = df["Text"].apply(lambda x: ner(x))

    # 3. Get the regions list
    regions_list = []

    for regions in df.Regions:
        regions_list.extend(regions)

    regions_list = list(set(regions_list))

    # 4. Get the region-country dict using OpenStreetMap API
    print("Getting the region-country dict...")
    region_country_dict = get_region_country_dict(regions_list)

    # 5. Map the regions to countries
    df["Regions"] = df["Regions"].apply(
        lambda x: [region_country_dict.get(region) for region in x]
    )
    df["Regions"] = [list(filter(None, lst)) for lst in df["Regions"]]

    # 6. Get the mode of the regions
    df["Mode"] = df["Regions"].apply(get_regions_mode)

    # 7. Map the source to country if the region is None
    df["Mode"] = df.apply(
        lambda row: source_country_dict[row["Source"]]
        if row["Mode"] == None
        else row["Mode"],
        axis=1,
    )

    return df
