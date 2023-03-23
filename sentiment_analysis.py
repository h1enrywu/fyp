import math, pandas as pd
from transformers import pipeline
from flair.models import TextClassifier
from flair.data import Sentence
from textblob import TextBlob

# Step 2
def flair_x_textblob(df):
    classifier = TextClassifier.load("en-sentiment")

    def predict(text):
        sentence = Sentence(text)
        classifier.predict(sentence)
        return sentence.labels[0].value, sentence.labels[0].score

    def get_subjectivity(text):
        return TextBlob(text).sentiment.subjectivity

    df[["Sentiment", "Confidence"]] = df["Text"].apply(lambda x: pd.Series(predict(x)))
    df["Subjectivity"] = df["Text"].apply(get_subjectivity)

    return df


# Main function
def sentiment_analysis(df):
    print("Performing sentiment analysis ...")

    # 1. Predict the emotion using Distilbert-Base-Uncased-Emotion
    classifier = pipeline(
        "text-classification",
        model="bhadresh-savani/distilbert-base-uncased-emotion",
        return_all_scores=True,
    )

    max_length = 512
    lists = [[], [], [], [], [], []]
    labels = ["sadness", "joy", "love", "anger", "fear", "surprise"]

    for text in df["Text"].tolist():
        # Split text into chunks of max_length
        num_chunks = math.ceil(len(text) / max_length)
        # Initialize lists to store scores for each label
        label_scores = [[] for _ in range(len(labels))]

        for i in range(num_chunks):
            start = i * max_length
            end = min((i + 1) * max_length, len(text))
            chunk = text[start:end]
            prediction = classifier(chunk)
            for label_idx, label in enumerate(labels):
                for pred_label in prediction[0]:
                    if pred_label["label"] == label:
                        label_scores[label_idx].append(pred_label["score"])
        final_scores = [
            sum(lst) / len(lst) if len(lst) > 0 else 0 for lst in label_scores
        ]
        for label, score, lst in zip(labels, final_scores, lists):
            lst.append(score)

    for lsts, label in zip(lists, labels):
        df.insert(len(df.columns), label, lsts)

    # 2. Predict sentiment and subjectivity using FLAIR and TextBlob respectively
    df = flair_x_textblob(df)

    return df
