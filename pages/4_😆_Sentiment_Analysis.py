import streamlit as st
from functions import hide_elements, get_map, create_word_cloud, logout_button
from streamlit_folium import st_folium
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt


# 1. page config and logout button
st.set_page_config(
    page_title="sentiment-analysis-fyp",
    layout="centered",
)
logout_button()

# 2. import the css file
with open("style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# 3. hide elements
hide_elements()

# 4. title
st.markdown(
    """
    <h2>Sentiment Analysis</h2>
    <h3>🙂 😠 😞 😂</h3>
    """,
    unsafe_allow_html=True,
)

# 5. read the dataset
df = pd.read_csv("analysis_ready.csv")
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

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
# df["Regions"] = df["Regions"].apply(lambda x: ast.literal_eval(x))

num_rows = df.shape[0]

# 6. initialize the session state
if "current_form" not in st.session_state:
    st.session_state.current_form = "None"

st.session_state.current_form = "Map"

if "current_country" not in st.session_state:
    st.session_state.current_country = "None"

if "current_frequency" not in st.session_state:
    st.session_state.current_frequency = "None"

st.session_state.current_fruq = "Half Year"

# 7. setting
with st.sidebar.expander("⚙️ Setting", expanded=True):
    interactive_form =  st.selectbox("Interactive with", ("Map", "Selection"), index=0)
    st.session_state.current_form = interactive_form

    freq_options = {"Month": ["M", "M1"], "Quarter": ["Q", "M3"], "Half Year": ["6M", "M6"]}
    fruq = st.selectbox("Frequency", list(freq_options.keys()), help="Only apply to line chart", index=2)
    st.session_state.current_fruq = fruq

# 8. date range filter
min_date = df['Date'].min()
max_date = df['Date'].max()

with st.sidebar.expander("📆 Date Range Filter", expanded=True):
    from_date = st.date_input(
        "From date",
        value=min_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )
    to_date = st.date_input(
        "To date",
        value=max_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )

    # filter the df
    from_datetime = pd.Timestamp(from_date)
    to_datetime = pd.Timestamp(to_date)

    df_filtered = df[(df["Date"] >= from_datetime) & (df["Date"] <= to_datetime)]
    new_num_rows = df_filtered.shape[0]

# 9. interactive map
if st.session_state.current_form == "Map":
    coordinates_country = {
        (-24.94685, 133.85727): "Australia",
        (35.13445, 102.69069): "China",
        (22.32667, 114.17228): "Hong Kong",
        (35.87259, 137.98691): "Japan",
        (1.36685, 103.86003): "Singapore",
        (36.53381, 127.83560): "South Korea",
        (55.08164, -2.61579): "United Kingdom",
        (39.74855, -101.19145): "United States",
    }

    with st.expander("🗺️ Interactive Map", expanded=True):
        map = get_map()
        st_data = st_folium(
            map, height=500, width=725, returned_objects=["last_object_clicked"]
        )

        st.info(
            "Reminder: You can select a country marker to display related analytics.", icon="👆"
        )

        if st_data["last_object_clicked"] is not None:
            lat, lng = (
                st_data["last_object_clicked"]["lat"],
                st_data["last_object_clicked"]["lng"],
            )

            # select the country
            if (lat, lng) in coordinates_country:
                st.session_state.current_country = coordinates_country[(lat, lng)]
                df_filtered = df_filtered[df_filtered["Mode"] == st.session_state.current_country]
                new_num_rows = df_filtered.shape[0]

# 10. visualization for interactive map
if st.session_state.current_country != "None" and st.session_state.current_form == "Map":
    st.markdown(
        f"""
        <br><h3>🌚 {st.session_state.current_country} 🌞</h3>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["Sentiment", "Emotions"])

    with tab1:
        # 10.1 pie chart
        sentiment_counts = df_filtered['Sentiment'].value_counts()

        fig = px.pie(sentiment_counts, 
                     values=sentiment_counts.values, 
                     names=sentiment_counts.index, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        
        fig.update_traces(
            textinfo='percent+label',
            hovertemplate="%{label}: %{value} (%{percent})",
            hole=.4,
            marker=dict(line=dict(color='#000000', width=1.5)),       
        )

        fig.update_layout(    
            legend=dict(
                x=0.5,
                xanchor="center",
                orientation='h'
            ),
            title=dict(
                text="Sentiment Distribution",
                x=0.5,
                y=0.95,
                xanchor="center",
                yanchor="top"
            ),
            margin=dict(t=70),
        )

        st.plotly_chart(fig)

        # 10.2 word cloud for positive sentiment
        text = " ".join(df_filtered[df_filtered["Sentiment"] == "POSITIVE"]["Text"].values)
        
        wordcloud = create_word_cloud(text, 30)

        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title("Top 30 Words in Positive Sentiment News")

        st.pyplot(plt)

        # 10.3 word cloud for negative sentiment
        text = " ".join(df_filtered[df_filtered["Sentiment"] == "NEGATIVE"]["Text"].values)

        wordcloud = create_word_cloud(text, 30)

        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title("Top 30 Words in Negative Sentiment News")

        st.pyplot(plt)

        # 10.4 line chart
        df_confidence = df_filtered.copy()
        df_confidence.loc[df_confidence["Sentiment"] == "NEGATIVE", "Confidence"] *= -1
    
        df_confidence = (
            df_confidence.groupby(pd.Grouper(key="Date", freq=freq_options[st.session_state.current_fruq][0]))
            .agg({"Confidence": "mean"})
            .reset_index()
        )

        fig = px.line(df_confidence, x="Date", y="Confidence")
        fig.update_traces(
            hovertemplate="Date: %{x}<br>" + "Score: %{y}",
            hoverlabel=dict(align="left"),
        )
        fig.update_layout(
            title=dict(
                text="Trend of Sentiment",
                x=0.5,
                xanchor="center",
                yanchor="top",
            ),
            xaxis=dict(title="Frequency", dtick=freq_options[st.session_state.current_fruq][1], tickformat="%m/%Y", tickangle=30),
            yaxis=dict(title="Score of Sentiment"),
            margin=dict(l=50, r=40),
        )

        st.plotly_chart(fig)   

    with tab2:
        # 10.5 radar chart
        labels = ["sadness", "joy", "love", "anger", "fear", "surprise"]
        avg_scores = []

        for label in labels:
            avg_score = df_filtered[label].mean()
            avg_scores.append(avg_score)

        fig = go.Figure(
            data=go.Scatterpolar(r=avg_scores, theta=labels, fill="toself", name="")
        )
        fig.update_traces(
            hovertemplate="Emotion: %{theta}<br>" + "Score: %{r}",
            hoverlabel=dict(align="left"),
        )
        fig.update_layout(
            title={
                "text": "Average Emotional Scores",
                "x": 0.5,
                "xanchor": "center",
                "y": 0.94,
            },
            polar=dict(
                angularaxis=dict(rotation=90),
                radialaxis=dict(visible=True, range=[0, 0.4]),
                gridshape="linear",
            ),
            margin=dict(t=90, b=35),
            showlegend=False,
        )

        st.plotly_chart(fig)
     
        # 10.6 line chart
        df_emotions = (
            df_filtered.groupby(pd.Grouper(key="Date", freq=freq_options[st.session_state.current_fruq][0]))
            .agg({"sadness": "mean", "joy": "mean", "love": "mean", "anger": "mean", "fear": "mean", "surprise": "mean"})
            .reset_index()
        )

        fig = go.Figure()

        for emotion in ["sadness", "joy", "love", "anger", "fear", "surprise"]:
            fig.add_trace(
                go.Scatter(x=df_emotions["Date"], y=df_emotions[emotion], name=emotion.capitalize())
            )

        fig.update_traces(
            hovertemplate="Date: %{x}<br>" + "Score: %{y}",
            hoverlabel=dict(align="left"),
        )
        fig.update_layout(
            title=dict(
                text="Trends of Emotions",
                x=0.5,
                xanchor="center",
                yanchor="top",
            ),
            xaxis=dict(title="Frequency", dtick=freq_options[st.session_state.current_fruq][1], tickformat="%m/%Y", tickangle=30),
            yaxis=dict(title="Emotion Score"),
            margin=dict(l=50, r=40),
        )

        st.plotly_chart(fig)
        
# 11. comparison
if st.session_state.current_form == "Selection":  
    st.session_state.current_country = "None"

    st.write("")

    options = st.multiselect(
        "Countries Selection",
        df_filtered["Mode"].unique(),
        df_filtered["Mode"].unique(),
        help="Select countries to display related analytics.",
    )

    # 11.1 based on the options selected, filter the dataframe
    df_filtered = df_filtered[df_filtered['Mode'].apply(lambda x: any([c in x for c in options]))]

    new_num_rows = df_filtered.shape[0]

    tab1, tab2 = st.tabs(["Sentiment", "Emotions"])

    with tab1:
        # 11.2 bar chart
        sentiment_counts = df_filtered.groupby(['Mode', 'Sentiment']).size().reset_index(name='count')

        sentiment_counts['Mode'] = pd.Categorical(sentiment_counts['Mode'])

        fig = px.bar(sentiment_counts, x="Mode", y="count", color="Sentiment", 
                    color_discrete_sequence=['Blue', 'Red'],
                    barmode='overlay',
        )  
        
        fig.update_traces(
            hovertemplate="%{x}: %{y}",
            hoverlabel=dict(align="left"),
        )
        fig.update_layout(
            title=dict(
                text="Sentiment Distribution",
                x=0.5,
                xanchor="center",
                yanchor="top",
            ),
            xaxis=dict(title="Countries"),
            yaxis=dict(title="Num of news articles"),
            margin=dict(l=50, r=40),
            bargap=0.6,
        )

        st.plotly_chart(fig)

        # 11.3 word cloud for positive sentiment
        text = " ".join(df_filtered[df_filtered["Sentiment"] == "POSITIVE"]["Text"].values)
        
        wordcloud = create_word_cloud(text, 50)

        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title("Top 50 Words in Positive Sentiment News")

        st.pyplot(plt)

        # 11.4 word cloud for negative sentiment
        text = " ".join(df_filtered[df_filtered["Sentiment"] == "NEGATIVE"]["Text"].values)

        wordcloud = create_word_cloud(text, 50)

        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title("Top 50 Words in Negative Sentiment News")

        st.pyplot(plt)

        # 11.5 line chart
        df_confidence = df_filtered.copy()
        df_confidence.loc[df_confidence["Sentiment"] == "NEGATIVE", "Confidence"] *= -1
        
        df_confidence = (
            df_confidence.groupby([pd.Grouper(key="Date", freq=freq_options[st.session_state.current_fruq][0]), "Mode"])
            .agg({"Confidence": "mean"})
            .reset_index()
        )

        fig = px.line(df_confidence, x="Date", y="Confidence", color="Mode")
        fig.update_traces(
            hovertemplate="Date: %{x}<br>" + "Score: %{y}<br>",
            hoverlabel=dict(align="left"),
        )
        fig.update_layout(
            title=dict(
                text="Trend of Sentiment",
                x=0.5,
                xanchor="center",
                yanchor="top",
            ),
            xaxis=dict(title="Month", dtick=freq_options[st.session_state.current_fruq][1], tickformat="%m/%Y", tickangle=45),
            yaxis=dict(title="Score of Sentiment"),
            margin=dict(l=50, r=40),
        )

        st.plotly_chart(fig)
 
    with tab2:
        # 11.4 radar chart
        grouped_data = df_filtered.groupby('Mode')

        labels = ["sadness", "joy", "love", "anger", "fear", "surprise"]

        traces = []

        for mode, data in grouped_data:
            avg_scores = []
            for label in labels:
                avg_score = data[label].mean()
                avg_scores.append(avg_score)

            trace = go.Scatterpolar(r=avg_scores, theta=labels, fill="toself", name=mode)
            traces.append(trace)

        fig = go.Figure(data=traces)

        fig.update_layout(
            title={
                "text": "Average Emotional Scores",
                "x": 0.5,
                "xanchor": "center",
                "y": 0.94,
            },
            polar=dict(
                angularaxis=dict(rotation=90),
                radialaxis=dict(visible=True, range=[0, 0.4]),
                gridshape="linear",
            ),
            margin=dict(t=90, b=35, l=150),
        )

        fig.update_traces(
            hovertemplate="Emotion: %{theta}<br>" + "Score: %{r}",
        )

        st.plotly_chart(fig)


        # 11.5 line chart
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Sadness", "Joy", "Love", "Anger", "Fear", "Surprise"])
        
        with tab1:
            df_emotions = (
                df_filtered.groupby([pd.Grouper(key="Date", freq=freq_options[st.session_state.current_fruq][0]), 'Mode'])
                .agg({"sadness": "mean"})
                .reset_index()
            )

            fig = go.Figure()

            for mode in df_emotions['Mode'].unique():
                fig.add_trace(
                    go.Scatter(x=df_emotions[df_emotions['Mode']==mode]["Date"], y=df_emotions[df_emotions['Mode']==mode]['sadness'], name=mode.capitalize())
                )

            fig.update_traces(
                hovertemplate="Date: %{x}<br>" + "Score: %{y}",
                hoverlabel=dict(align="left"),
            )
            fig.update_layout(
                title=dict(
                    text="Trends of Sadness",
                    x=0.5,
                    xanchor="center",
                    yanchor="top",
                ),
                xaxis=dict(title="Frequency", dtick=freq_options[st.session_state.current_fruq][1], tickformat="%m/%Y", tickangle=30),
                yaxis=dict(title="Sadness Score"),
                margin=dict(l=50, r=40),
            )

            st.plotly_chart(fig)

        with tab2:
            df_emotions = (
                df_filtered.groupby([pd.Grouper(key="Date", freq=freq_options[st.session_state.current_fruq][0]), 'Mode'])
                .agg({"joy": "mean"})
                .reset_index()
            )

            fig = go.Figure()

            for mode in df_emotions['Mode'].unique():
                fig.add_trace(
                    go.Scatter(x=df_emotions[df_emotions['Mode']==mode]["Date"], y=df_emotions[df_emotions['Mode']==mode]['joy'], name=mode.capitalize())
                )

            fig.update_traces(
                hovertemplate="Date: %{x}<br>" + "Score: %{y}",
                hoverlabel=dict(align="left"),
            )
            fig.update_layout(
                title=dict(
                    text="Trends of Joy",
                    x=0.5,
                    xanchor="center",
                    yanchor="top",
                ),
                xaxis=dict(title="Frequency", dtick=freq_options[st.session_state.current_fruq][1], tickformat="%m/%Y", tickangle=30),
                yaxis=dict(title="Joy Score"),
                margin=dict(l=50, r=40),
            )

            st.plotly_chart(fig)

        with tab3:
            df_emotions = (
                df_filtered.groupby([pd.Grouper(key="Date", freq=freq_options[st.session_state.current_fruq][0]), 'Mode'])
                .agg({"love": "mean"})
                .reset_index()
            )

            fig = go.Figure()

            for mode in df_emotions['Mode'].unique():
                fig.add_trace(
                    go.Scatter(x=df_emotions[df_emotions['Mode']==mode]["Date"], y=df_emotions[df_emotions['Mode']==mode]['love'], name=mode.capitalize())
                )

            fig.update_traces(
                hovertemplate="Date: %{x}<br>" + "Score: %{y}",
                hoverlabel=dict(align="left"),
            )
            fig.update_layout(
                title=dict(
                    text="Trends of Love",
                    x=0.5,
                    xanchor="center",
                    yanchor="top",
                ),
                xaxis=dict(title="Frequency", dtick=freq_options[st.session_state.current_fruq][1], tickformat="%m/%Y", tickangle=30),
                yaxis=dict(title="Love Score"),
                margin=dict(l=50, r=40),
            )

            st.plotly_chart(fig)

        with tab4:
            df_emotions = (
                df_filtered.groupby([pd.Grouper(key="Date", freq=freq_options[st.session_state.current_fruq][0]), 'Mode'])
                .agg({"anger": "mean"})
                .reset_index()
            )

            fig = go.Figure()

            for mode in df_emotions['Mode'].unique():
                fig.add_trace(
                    go.Scatter(x=df_emotions[df_emotions['Mode']==mode]["Date"], y=df_emotions[df_emotions['Mode']==mode]['anger'], name=mode.capitalize())
                )

            fig.update_traces(
                hovertemplate="Date: %{x}<br>" + "Score: %{y}",
                hoverlabel=dict(align="left"),
            )
            fig.update_layout(
                title=dict(
                    text="Trends of Anger",
                    x=0.5,
                    xanchor="center",
                    yanchor="top",
                ),
                xaxis=dict(title="Frequency", dtick=freq_options[st.session_state.current_fruq][1], tickformat="%m/%Y", tickangle=30),
                yaxis=dict(title="Anger Score"),
                margin=dict(l=50, r=40),
            )

            st.plotly_chart(fig)

        with tab5:
            df_emotions = (
                df_filtered.groupby([pd.Grouper(key="Date", freq=freq_options[st.session_state.current_fruq][0]), 'Mode'])
                .agg({"fear": "mean"})
                .reset_index()
            )

            fig = go.Figure()

            for mode in df_emotions['Mode'].unique():
                fig.add_trace(
                    go.Scatter(x=df_emotions[df_emotions['Mode']==mode]["Date"], y=df_emotions[df_emotions['Mode']==mode]['fear'], name=mode.capitalize())
                )

            fig.update_traces(
                hovertemplate="Date: %{x}<br>" + "Score: %{y}",
                hoverlabel=dict(align="left"),
            )
            fig.update_layout(
                title=dict(
                    text="Trends of Fear",
                    x=0.5,
                    xanchor="center",
                    yanchor="top",
                ),
                xaxis=dict(title="Frequency", dtick=freq_options[st.session_state.current_fruq][1], tickformat="%m/%Y", tickangle=30),
                yaxis=dict(title="Fear Score"),
                margin=dict(l=50, r=40),
            )

            st.plotly_chart(fig)

        with tab6:
            df_emotions = (
                df_filtered.groupby([pd.Grouper(key="Date", freq=freq_options[st.session_state.current_fruq][0]), 'Mode'])
                .agg({"surprise": "mean"})
                .reset_index()
            )

            fig = go.Figure()

            for mode in df_emotions['Mode'].unique():
                fig.add_trace(
                    go.Scatter(x=df_emotions[df_emotions['Mode']==mode]["Date"], y=df_emotions[df_emotions['Mode']==mode]['surprise'], name=mode.capitalize())
                )

            fig.update_traces(
                hovertemplate="Date: %{x}<br>" + "Score: %{y}",
                hoverlabel=dict(align="left"),
            )
            fig.update_layout(
                title=dict(
                    text="Trends of Surprise",
                    x=0.5,
                    xanchor="center",
                    yanchor="top",
                ),
                xaxis=dict(title="Frequency", dtick=freq_options[st.session_state.current_fruq][1], tickformat="%m/%Y", tickangle=30),
                yaxis=dict(title="Surprise Score"),
                margin=dict(l=50, r=40),
            )

            st.plotly_chart(fig)

# 12. dataset statistic
with st.sidebar.expander("📈 Dataset Statistic", expanded=True):
    delta = None
    if new_num_rows != num_rows:
        delta = new_num_rows - num_rows
    st.metric(
        "Num of articles",
        new_num_rows,
        delta=delta,
        # help="The number of articles after filtering.",
    )
    num_rows = new_num_rows







    
        