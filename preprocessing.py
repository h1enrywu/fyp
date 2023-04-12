import re, en_core_web_sm, requests, urllib.parse
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from statistics import mode



def cleaning(data):
    # Remove punctuation
    data = re.sub("[^a-zA-Z]", " ", data)

    # Lowercasing
    data = data.lower()

    # Tokenizing
    words = word_tokenize(data)

    # Remove stopwords
    stopwords_list = requests.get(
        "https://gist.githubusercontent.com/rg089/35e00abf8941d72d419224cfd5b5925d/raw/12d899b70156fd0041fa9778d657330b024b959c/stopwords.txt"
    ).content
    stopwords = set(stopwords_list.decode().splitlines())
    words = [word for word in words if not word in stopwords]

    # Lemmatizing
    lem = WordNetLemmatizer()
    words = [lem.lemmatize(word) for word in words]

    # Back to a String
    cleaned_data = " ".join(words)

    return cleaned_data


def ner(data):
    # Load the model
    nlp = en_core_web_sm.load()
    # Process the text with the model
    doc = nlp(data)
    # Return a list of all GPE entities found in the text
    return [ent.text for ent in doc.ents if ent.label_ == "GPE"]



def get_region_country_dict(regions_list):
    # This nested function takes a GPE (Geographical Entity) and returns the corresponding country name
    def get_country_name(region_name):
        # Encode the GPE to make it URL-friendly
        encoded_city_name = urllib.parse.quote(region_name)
        # Set the request headers to ensure that the response is in English
        headers = {"accept-language": "en"}
        # Construct the API URL
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_city_name}&format=json&limit=1"
        # Send the API request and get the response
        response = requests.get(url, headers=headers)
        # If the response is successful
        if response.status_code == 200:
            # Get the JSON data from the response
            data = response.json()
            # If the JSON data is not empty
            if len(data) > 0:
                # Extract the country name from the API response
                country_name = data[0]["display_name"].split(",")[-1].strip()
                # If the GPE is the region from Hong Kong, return "Hong Kong" instead of "China"
                if "Hong Kong" in data[0]["display_name"]:
                    return "Hong Kong"
                else:
                    return country_name
        # If no country name is found, return None
        return None

    # Initialize an empty dictionary to store the region-country mappings
    region_country_dict = {}

    for region in regions_list:
        # If the GPE is valid
        if region.isalpha() or " " in region:
            # Get the country name corresponding to the GPE
            country_name = get_country_name(region)
            # If a country name is found
            if country_name:
                # Add the region-country mapping to the dictionary
                region_country_dict[region] = country_name
            # If no country name is found
            else:
                # Map the region to None
                region_country_dict[region] = None
        # If the GPE is invalid
        else:
            # Map the region to None
            region_country_dict[region] = None
    return region_country_dict


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
    # 1. Data cleaning
    print("Data cleaning...")
    df["Cleaned_Title"] = df["Title"].apply(cleaning)
    df["Cleaned_Content"] = df["Content"].apply(cleaning)
    df["Text"] = df["Cleaned_Title"] + " " + df["Cleaned_Content"]

    # 2. NER
    print("Performing NER...")
    # 2.1 Perform NER
    df["Regions"] = df["Content"].apply(lambda x: ner(x))

    # 2.2 Creates a unique list of GPE (Geographical Entity)
    regions_list = []
    for regions in df.Regions:
        regions_list.extend(regions)
    regions_list = list(set(regions_list))

    # 2.3 Get the region-country dict using OpenStreetMap API
    print("Getting the region-country dict...")
    region_country_dict = get_region_country_dict(regions_list)

    # 2.4 Map the regions to countries
    df["Regions"] = df["Regions"].apply(
        lambda x: [region_country_dict.get(region) for region in x]
    )
    df["Regions"] = [list(filter(None, lst)) for lst in df["Regions"]]

    # 2.5 Get the mode of the column "Regions"
    def get_regions_mode(x):
        if x:
            return mode(x)
        else:
            return None
    df["Mode"] = df["Regions"].apply(get_regions_mode)

    # 2.6 Map the source to country if the column "Regions" is empty
    df["Mode"] = df.apply(
        lambda row: source_country_dict[row["Source"]]
        if row["Mode"] == None
        else row["Mode"],
        axis=1,
    )

    return df

