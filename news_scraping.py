import requests, pandas as pd
from bs4 import BeautifulSoup as bs
from nltk.stem.porter import *


m_dict = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12",
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12",
    "Sept": "09",
}


def news_scraping() -> None:
    # Read urls.csv
    urls_df = pd.read_csv("urls.csv")
    # Drop duplicates
    urls_df.drop_duplicates(subset=["URL"], inplace=True)
    # Count the number of unscraped articles
    unscraped_count = len(urls_df[urls_df["Scraped"] == 0])
    # Remove the articles that have been skipped
    df_urls = urls_df[urls_df["Skipped"] != 1]
    # Create a data frame to store the scraped articles in this run
    df = pd.DataFrame(columns=["Source", "URL", "Title", "Date", "Content"], index=None)
    print("Articles scraping started...\n")

    # Excluded sources, used for testing
    excluded_sources = [
        # "bbc",
        # "cnn",
        # "thestandard",
        # "rthk",
        # "yomiuri",
        # "asahi",
        # "mainichi",
        # "japantimes",
        # "koreaherald",
        # "koreatimes",
        # "koreajoongangdaily",
        # "hkfp",
        # "theguardian",
        # "dailymail",
        # "foxnews",
        # "news.com.au",
        # "abc",
        # "straitstimes",
        # "todayonline",
    ]
    if excluded_sources:
        for source in excluded_sources:
            df_urls = df_urls[df_urls["Source"] != source]

    # Loop through the URLs
    for row in df_urls.itertuples():

        # If the article has been scraped, skip it
        if row.Scraped == 1:
            continue

        # Get the soup of the article
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
        }
        response = requests.get(row.URL, headers=headers)
        soup = bs(response.text, "lxml")
        print(row.URL)

        # Handle the articles from BBC
        if row.Source == "bbc":
            # Skip the articles that are not in English
            if "pidgin" in row.URL or "afaanoromoo" in row.URL:
                # Mark special cases as skipped
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue

            # For BBC, if the URL contains any of the keywords, the HTML structure for the title, date and body are different
            keywords = ["/future/", "/culture/", "/travel/"]
            if any(keyword in row.URL for keyword in keywords):
                # Scrpae the title
                title = soup.select(
                    ".article-headline__text.b-reith-sans-font.b-font-weight-300"
                )[0].text
                # Scrape the date and format it
                date = soup.select(".b-font-family-serif.b-font-weight-300")[0]
                date = date.text.split(" ")
                day = "0" + date[0][:-2] if int(date[0][:-2]) < 10 else date[0][:-2]
                date = date[2] + "-" + m_dict[date[1]] + "-" + day
                # Scrape the body
                body = soup.select(".article__body-content p")
                body = " ".join([p.text.strip() for p in body])
            else:
                title = soup.select(".ssrcss-15xko80-StyledHeading.e1fj1fc10")[0].text
                date = soup.find(attrs={"data-testid": "timestamp"})["datetime"]
                date = date.split("T")[0]
                body = soup.select(".ssrcss-pv1rh6-ArticleWrapper.e1nh2i2l6 p")
                body = " ".join([p.text.strip() for p in body])

            # Raise an error if any of the scraped elements is empty
            elements = ["bbc", row.URL, title, date, body]
            if not all(elements):
                raise ValueError

            # Append the scraped elements to the data frame
            df.loc[len(df)] = elements

        elif row.Source == "cnn":
            keywords = ["/videos/", "/live-news/", "/gallery/"]
            if any(keyword in row.URL for keyword in keywords):
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            try:
                if "/style/" in row.URL:
                    title = soup.select(".PageHead__title")[0].text
                    date = soup.select(".PageHead__published")[0].text.split(" ")
                    day = "0" + date[1][:-2] if int(date[1][:-2]) < 10 else date[1][:-2]
                    date = date[3] + "-" + m_dict[date[2]] + "-" + day
                    body = soup.select(".BasicArticle__main")[0].text
                else:
                    title = soup.select(".headline__text.inline-placeholder")[0]
                    title = title.text.strip()
                    date = soup.select(".timestamp")[0].text.strip().split(" ")
                    day = (
                        "0" + date[-2][:-1]
                        if int(date[-2][:-1]) < 10
                        else date[-2][:-1]
                    )
                    date = date[-1] + "-" + m_dict[date[-3]] + "-" + day
                    body = soup.select(".article__main p")
                    body = " ".join([p.text.strip() for p in body])
            except IndexError:
                title = soup.select(".pg-headline")[0].text
                date = soup.select(".update-time")[0].text.split(" ")
                try:
                    day = (
                        "0" + date[-3][:-1]
                        if int(date[-3][:-1]) < 10
                        else date[-3][:-1]
                    )
                    date = date[-2] + "-" + m_dict[date[-4]] + "-" + day
                except ValueError:
                    date = soup.find("meta", {"property": "og:pubdate"})["content"][:10]
                body = soup.select(".l-container .zn-body__paragraph")
                body = " ".join([p.text.strip() for p in body])
            elements = ["cnn", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "thestandard":
            if "/archive/" in row.URL:
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            title = soup.select(".heading.clearfix h1")[0].text
            date = soup.select("span.pull-left")[0].text.split(" ")
            if soup.select(".writer") == []:
                date = date[4] + "-" + m_dict[date[3]] + "-" + date[2]
            else:
                date = date[-1] + "-" + m_dict[date[-2]] + "-" + date[-3]
            body = soup.select(".content p")
            body = " ".join([p.text.strip() for p in body])
            elements = ["thestandard", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "rthk":
            title = soup.select(".itemTitle")[0].text.strip()
            date = soup.select(".createddate")[0].text.split(" ")[0]
            body = soup.select(".itemFullText")[0].text.strip()

            elements = ["rthk", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "hkfp":
            if "/author/" in row.URL:
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            title = soup.select(".entry-header h1")[0].text.strip()
            date = soup.find("time")["datetime"].split("T")[0]
            body = soup.select(".entry-content p")
            body = " ".join([p.text.strip() for p in body])
            elements = ["hkfp", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "yomiuri":
            if "/weekly/" in row.URL:
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            title = soup.select(".bloc_1 h1")[0].text
            date = soup.select(".postdate")[0].text.split(",")
            year = date[-1].strip()
            date = date[1].strip().split(" ")
            day = "0" + date[1] if int(date[1]) < 10 else date[1]
            date = year + "-" + m_dict[date[0]] + "-" + day
            body = soup.select("#p-article-block p")
            body = " ".join([p.text.strip() for p in body[2:]])
            elements = ["yomiuri", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "asahi":
            title = soup.select(".Title h1")[0].text.strip()
            date = soup.select(".EnLastUpdated")[0].text.split(" ")
            day = "0" + date[1][:-1] if int(date[1][:-1]) < 10 else date[1][:-1]
            date = date[2] + "-" + m_dict[date[0]] + "-" + day
            body = soup.select(".ArticleText p")
            body = " ".join([p.text.strip() for p in body])
            elements = ["asahi", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "mainichi":
            if ("/graphs/" in row.URL) or (
                soup.select(".articledetail-head-shoulder") != []
            ):
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            title = soup.select("#main-cont header h1")[0].text
            date = soup.select("time")[0].text.split(" ")
            day = "0" + date[1][:-1] if int(date[1][:-1]) < 10 else date[1][:-1]
            date = date[2] + "-" + m_dict[date[0]] + "-" + day
            body = soup.select(".main-text .txt")
            body = " ".join([p.text.strip() for p in body])
            elements = ["mainichi", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "japantimes":
            if (
                soup.select(".header-title")[0].text.strip() == "Article expired"
                or "/cartoons/" in row.URL
                or "/liveblogs/" in row.URL
            ):
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            if "/photo-essay-" in row.URL:
                title = soup.select(".padding_block h1")[0].text
                date = soup.find(attrs={"property": "DC.date.issued"})["content"]
                date = date.split("T")[0]
                body = soup.select("article p")
                body = " ".join([p.text.strip() for p in body])
            else:
                try:
                    title = soup.select(".padding_block.single-title h1")[0].text
                except IndexError:
                    title = soup.select(".padding_block.single-post-title h1")[0].text
                date = soup.select("time")[0].text.strip().split(" ")
                day = "0" + date[1][:-1] if int(date[1][:-1]) < 10 else date[1][:-1]
                date = date[2] + "-" + m_dict[date[0]] + "-" + day
                body = soup.select("#jtarticle p")
                body = " ".join([p.text.strip() for p in body])
            elements = ["japantimes", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "koreaherald":
            if "/kpopherald." in row.URL:
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            title = soup.select(".view_tit")[0].text.strip()
            date = soup.select(".view_tit_byline_r")[0].text
            date = date.split(" : ")[2].split(" ")
            day = "0" + date[1][:-1] if int(date[1][:-1]) < 10 else date[1][:-1]
            date = date[2] + "-" + m_dict[date[0]] + "-" + day
            body = soup.select(".view_con_t")
            body = " ".join([p.text.strip() for p in body])
            elements = ["koreaherald", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "koreatimes":
            if "/dr/" in row.URL:
                title = soup.select(".DR_headline")[0].text.strip()
                date = soup.select(".DR_view_date span")[0].text
                date = date.split(" : ")[1].split("\xa0")[0]
                body = soup.select(".caption_photo")
                body = " ".join([p.text.strip() for p in body])
            else:
                title = soup.select(".view_headline.LoraMedium")[0].text.strip()
                if "DAILY FORTUNE" in title:
                    urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                    continue
                date = soup.select(".view_date")[1].text
                date = date.split(" : ")[1].split("\xa0")[0]
                body = soup.select("#startts span")
                body = " ".join([p.text.strip() for p in body])
            elements = ["koreatimes", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "koreajoongangdaily":
            title = soup.select(".view-article-title.serif")[0].text
            date = row.URL.split("/", 6)
            date = date[3] + "-" + date[4] + "-" + date[5]
            if len(date) > 10:
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            body = soup.select("div#article_body")[0].text.strip()
            elements = [
                "koreajoongangdaily",
                row.URL,
                title,
                date,
                body,
            ]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "theguardian":
            title = None
            if "/gallery/" in row.URL or "/video/" in row.URL:
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            classes = [
                ".dcr-1b0zxa5",
                ".dcr-y70mar",
                ".dcr-1xaevyx",
                ".dcr-1kwg2vo",
                ".content__headline",
                ".dcr-gp80yp",
                ".dcr-186f9ox",
                ".dcr-m6jbyb",
                ".dcr-18ogzt",
                ".dcr-1ttbui0",
                ".dcr-d3raws",
                ".dcr-17joxcd",
            ]
            for c in classes:
                try:
                    title = soup.select(c)[0].text
                    break
                except IndexError:
                    pass
            if "Sorry" in title:
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            try:
                date = soup.select(".dcr-u0h1qy")[0].text.split(" ")
            except IndexError:
                date = soup.select(".dcr-eb59kw")[0].text.split(" ")
            day = "0" + date[1] if int(date[1]) < 10 else date[1]
            date = date[3] + "-" + m_dict[date[2]] + "-" + day
            body = soup.select("#maincontent p")
            body = " ".join([p.text.strip() for p in body])
            elements = ["theguardian", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "dailymail":
            if "/best-buys/" in row.URL:
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            title = soup.select("#js-article-text h2")[0].text
            date = soup.select(".article-timestamp.article-timestamp-updated time")[0][
                "datetime"
            ]
            date = date.split("T")[0]
            body = soup.select("#js-article-text p")
            body = " ".join([p.text.strip() for p in body])
            elements = ["dailymail", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "foxnews":
            if "/radio." in row.URL:
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            title = soup.select(".headline")[0].text
            date = soup.select(".article-date time")[0].text.split(" ")
            date = date[3] + "-" + m_dict[date[1]] + "-" + date[2][:-1]
            body = soup.select(".article-content p")
            body = " ".join([p.text.strip() for p in body])
            elements = ["foxnews", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "news.com.au":
            if "/video/" in row.URL:
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            title = soup.select("#story-headline")[0].text
            date = soup.select("#publish-date")[0].text.split(" ")
            day = "0" + date[1][:-1] if int(date[1][:-1]) < 10 else date[1][:-1]
            date = date[2] + "-" + m_dict[date[0]] + "-" + date[1][:-1]
            body = soup.select("#story-primary p")
            body = " ".join([p.text.strip() for p in body])
            elements = ["news.com.au", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "abc":
            keywords = ["/radio/", "/triplej/", "/everyday/", "/btn/", "/abckids/"]
            if (
                any([k in row.URL for k in keywords])
                or soup.select(".MastheadCTA_ctaText__0FDRQ") != []
            ):
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue
            keywords = ["/perth/", "/religion/", "/melbourne/"]
            if any([k in row.URL for k in keywords]):
                title = soup.select(".DetailHeader_meta__75lvM h1")[0].text
                date = soup.select("time.ScreenReaderOnly_srOnly__aJfWv")[0]["datetime"]
                date = date.split("T")[0]
                body = soup.select(".DetailLayout_inner__BwjPC p")
                body = " ".join([p.text.strip() for p in body])
            else:
                title = soup.select(
                    ".YtLlr.u5PGL.kikHg.v9jdb.bpUid.g0Ocq.LS87j.RDGP5.Z5947._5pKBM.HXgQg"
                )[0].text
                if "VIDEO:" in title or "The Loop:" in title:
                    urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                    continue
                date = soup.find("meta", {"property": "article:published_time"})[
                    "content"
                ][:10]
                body = soup.select("#body p")
                body = " ".join([p.text.strip() for p in body])
            elements = ["abc", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "straitstimes":
            if (
                "/interactive" in row.URL
                or "/multimedia/" in row.URL
                or "/stomp." in row.URL
            ):
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue

            title = soup.select(".headline.node-title")[0].text.strip()
            date = soup.find("meta", {"property": "article:published_time"})["content"][
                :10
            ]
            body = soup.select(".ds-field-item p")
            body = " ".join([p.text.strip() for p in body])

            elements = ["straitstimes", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        elif row.Source == "todayonline":
            if "/minute/" in row.URL:
                urls_df.loc[urls_df.URL == row.URL, "Skipped"] = 1
                continue

            title = soup.select(".h1.h1--page-title")[0].text.strip()
            date = soup.select(".article__row.article__row--")[0].text.split(" ")
            day = "0" + date[2][:-1] if int(date[2][:-1]) < 10 else date[2][:-1]
            date = date[3] + "-" + m_dict[date[1]] + "-" + day
            body = soup.select(".text-long p")
            body = " ".join([p.text.strip() for p in body])

            elements = ["todayonline", row.URL, title, date, body]
            if not all(elements):
                raise ValueError
            df.loc[len(df)] = elements

        else:
            raise ValueError

        # Mark the all scraped urls as scraped
        urls_df.loc[urls_df.URL == row.URL, "Scraped"] = 1

    print("\nArticles scraping completed.")
    print(f"{unscraped_count} unscraped urls were found.")
    print(f"{len(urls_df[urls_df.Skipped == 1])} urls were skipped.")
    print(f"{len(df)} new articles were scraped gross.\n")

    # Sort the "urls_df" dataframe by "Source"
    urls_df = urls_df.sort_values(by="Source")
    # Update the "Skipped" and "Scraped" columns for each URL in the urls.csv file
    urls_df.to_csv("urls.csv", index=False)
    # Convert the "Date" column to datetime format
    df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d")
    # Sort the "df" dataframe by "Source"
    df = df.sort_values(by="Source")
    # Append the scraped articles to the news.csv file
    df.to_csv("news.csv", mode="a", index=False, header=False)

    return None



