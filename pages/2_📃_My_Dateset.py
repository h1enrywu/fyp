import streamlit as st
from functions import hide_elements, logout_button
import pandas as pd
import plotly.express as px


# 1. clear the cache
st.session_state.current_country = "None"

# 2. page config and logout button
st.set_page_config(
    page_title="my-dateset-fpy",
    layout="centered",
)
logout_button()

# 3. import the css file
with open("style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# 4. hide elements
hide_elements()

# 5. title
st.markdown(
    """
    <h2>Dataset Description</h2><br>
    """,
    unsafe_allow_html=True,
)

# 6. initialize the session state
if "current_frequency" not in st.session_state:
    st.session_state.current_frequency = "None"

st.session_state.current_fruq = "Half Year"

# 7. frequency
freq_options = {"Month": ["M", "M1"], "Quarter": ["Q", "M3"], "Half Year": ["6M", "M6"]}
fruq = st.sidebar.selectbox(
    "Frequency", list(freq_options.keys()), help="Only apply to line chart", index=2
)
st.session_state.current_fruq = fruq

tab1, tab2 = st.tabs(["Raw Dataset", "Analysis-ready Dataset"])

# 8. raw dataset
with tab1:
    # 8.1 description
    with st.expander("Dataset", expanded=True):
        df = pd.read_csv("news.csv")
        st.write(len(df))
        df["Date"] = pd.to_datetime(df["Date"], format='%d/%m/%Y')
        st.dataframe(df)

        content = """
        <div class="my_container" >
            <p><b>Description</b> : the above dataset is the raw dataset without preprocessing and analysis.</p>
            <ul>
                <li><b>Source</b> : the source of the article</li>
                <li><b>URL</b> : the URL of the article</li>
                <li><b>Title</b> : the title of the article</li>
                <li><b>Date</b> : the publish date of the article</li>
                <li><b>Content</b> : the content of the article</li>
            </ul>
        </div>
        <br>
        """
        st.markdown(content, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.metric("Num of Articles", df.shape[0])
        col2.metric("Num of Sources", df.Source.nunique())

    # 8.2. line chart
    monthly_counts = df.groupby(
        pd.Grouper(key="Date", freq=freq_options[st.session_state.current_fruq][0])
    ).size()

    fig = px.line(x=monthly_counts.index, y=monthly_counts.values, markers=True)
    fig.update_traces(
        hovertemplate="Month: %{x|%m/%Y}<br>Count: %{y}",
        hoverlabel=dict(align="left"),
    )
    fig.update_layout(
        title=dict(
            text="Trends in the Num of News Articles",
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        xaxis=dict(
            title="Date",
            dtick=freq_options[st.session_state.current_fruq][1],
            tickformat="%m/%Y",
            tickangle=30,
        ),
        yaxis=dict(title="Num of news articles"),
        margin=dict(l=50, r=40),
    )

    st.plotly_chart(fig)

    # 8.3.v1 bar chart
    region_sources = {
        "United Kingdom": ["bbc", "theguardian", "dailymail"],
        "United States": ["cnn", "foxnews"],
        "Hong Kong": ["thestandard", "rthk", "hkfp"],
        "Japan": ["yomiuri", "asahi", "mainichi", "japantimes"],
        "South Korea": ["koreaherald", "koreatimes", "koreajoongangdaily"],
        "Australia": ["news.com.au", "abc"],
        "Singapore": ["straitstimes", "todayonline"],
    }

    data = []
    for region, sources in region_sources.items():
        for source in sources:
            count = df[df.Source == source].shape[0]
            data.append({"Region": region, "Source": source, "Count": count})

    df_region_sources = pd.DataFrame(data)

    fig = px.bar(
        df_region_sources,
        x="Region",
        y="Count",
        color="Source",
        orientation="v",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )  # px.colors.sequential.RdBu

    fig.update_traces(
        hovertemplate="%{x}: %{y}",
        hoverlabel=dict(align="left"),
    )

    fig.update_layout(
        title=dict(
            text="Proportion of Sources",
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        xaxis=dict(title="Region", tickangle=30),
        yaxis=dict(title="Count"),
        showlegend=True,
        margin=dict(l=50, r=40),
        bargap=0.6,
    )

    # st.plotly_chart(fig, use_container_width=True)

    # 8.3.v2 sunburst chart
    import plotly.express as px
    import pandas as pd

    region_sources = {
        "United Kingdom": ["bbc", "theguardian", "dailymail"],
        "United States": ["cnn", "foxnews"],
        "Hong Kong": ["thestandard", "rthk", "hkfp"],
        "Japan": ["yomiuri", "asahi", "mainichi", "japantimes"],
        "South Korea": ["koreaherald", "koreatimes", "koreajoongangdaily"],
        "Australia": ["news.com.au", "abc"],
        "Singapore": ["straitstimes", "todayonline"],
    }

    data = []
    for region, sources in region_sources.items():
        for source in sources:
            count = df[df.Source == source].shape[0]
            data.append({"Region": region, "Source": source, "Count": count})

    df_region_sources = pd.DataFrame(data)

    total_count = df_region_sources["Count"].sum()

    fig = px.sunburst(
        df_region_sources,
        path=["Region", "Source"],
        values="Count",
        color="Region",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hover_data={"Count": ":,"},
        branchvalues="total",
    )

    fig.update_layout(
        title=dict(
            text="Proportion of Sources",
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        margin=dict(t=70, b=30),
    )

    for r in fig["data"]:
        r["textinfo"] = "label+percent parent"
        r["hovertemplate"] = ("%{label}: %{value} (%{percentParent:.0%})",)

    st.plotly_chart(fig, use_container_width=True)

# 9. analysis-ready dataset
with tab2:
    # 9.1. description
    with st.expander("Dataset", expanded=True):
        df = pd.read_csv("analysis_ready.csv")
        # df["Date"] = pd.to_datetime(df["Date"])
        df = df.drop(columns=["Title", "URL", "Content", "Regions"])
        countries = [
            "Australia",
            "China",
            "Hong Kong",
            "Japan",
            "Singapore",
            "South Korea",
            "United Kingdom",
            "United States",
        ]
        df = df[df["Mode"].isin(countries)]
        st.dataframe(df)

        content = """
        <div class="my_container" >
            <p>
                <b>Description</b> :
                the above dataset is the new version of the raw dataset with preprocessing and sentiment analysis.
            </p>
            <ul>
                <li>
                    <b>Source</b> :
                    the source of the article
                </li>
                <li>
                    <b>Date</b> : 
                    the publish date of the article
                </li>
                <li>
                    <b>Text</b> : 
                    the concatenation of the title and content of the article after preprocessing
                </li>
                <li>
                    <b>Mode</b> : 
                    the country or region most relevant to the article. I chose 8 countries [Australia, China, Hong Kong, Japan, Singapore, South Korea, United Kingdom, United States] for the further visualization.
                </li>
                <li>
                    <b>sadness / joy / love / anger / fear / surprise</b> : 
                    the emotional score of the article, ranges from 0 to 1. The higher score, the more emotion the article expressed.
                </li>
                <li>
                    <b>Sentiment</b> :
                    the sentiment of the article, with three possible values [POSITIVE, NEGATIVE, NEUTRAL].
                </li>
                <li>
                    <b>Confidence</b> :
                    the confidence score of the article, ranges from 0 to 1. The higher score, the more confident the sentiment analysis.
                </li>
                <li>
                    <b>Subjectivity</b> :
                    the subjectivity score of the article, ranges from 0 to 1. The higher score, the more subjective the article.
                </li>                
            </ul>
        </div>
        <br>
        """
        st.markdown(content, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.metric(
            "Num of Articles",
            df.shape[0],
            # help="The number of articles has dropped due to country/region filtering.",
        )
        col2.metric("Num of Countries", len(df.Mode.unique()))

    # 9.2. box chart
    fig = px.box(
        df,
        x="Source",
        y="Subjectivity",
        orientation="v",
        color="Source",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_layout(
        title=dict(
            text="Subjectivity of Different Sources",
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        xaxis=dict(title="Sources", tickangle=30),
        margin=dict(l=50, r=40),
    )

    st.plotly_chart(fig)

    # 9.3. scratter chart
    fig = px.scatter(
        df,
        x="Confidence",
        y="Subjectivity",
        color="Confidence",
        trendline="ols",
        trendline_color_override="red",
    )
    fig.update_traces(
        hovertemplate="Confidence: %{x}<br>" + "Subjectivity: %{y}",
        hoverlabel=dict(align="left"),
    )
    fig.update_layout(
        title=dict(
            text="Relationship between Confidence and Subjectivity",
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        margin=dict(l=50, r=40),
    )

    st.plotly_chart(fig)