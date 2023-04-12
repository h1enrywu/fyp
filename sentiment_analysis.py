import math, pandas as pd
from transformers import pipeline
from flair.models import TextClassifier
from flair.data import Sentence
from textblob import TextBlob


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
    # 1. Predict the emotion using Distilbert-Base-Uncased-Emotion
    print("Performing sentiment analysis ...")
    # Load the pre-trained emotion classification model
    classifier = pipeline(
        "text-classification",
        model="bhadresh-savani/distilbert-base-uncased-emotion",
        return_all_scores=True,
    )

    # Define the maximum length of text chunks to process
    max_length = 512

    # Initialize empty lists to store scores for each label and define the labels for each emotion category
    lists = [[], [], [], [], [], []]
    labels = ["sadness", "joy", "love", "anger", "fear", "surprise"]

    # Loop over each text in the input DataFrame
    for text in df["Text"].tolist():
        # Split text into chunks of max_length
        num_chunks = math.ceil(len(text) / max_length)

        # Initialize lists to store scores for each label
        label_scores = [[] for _ in range(len(labels))]

        # Loop over each text chunk
        for i in range(num_chunks):
            start = i * max_length
            end = min((i + 1) * max_length, len(text))
            chunk = text[start:end]

            # Get the emotion scores for the current chunk
            prediction = classifier(chunk)

            # Store the scores for each label
            for label_idx, label in enumerate(labels):
                for pred_label in prediction[0]:
                    if pred_label["label"] == label:
                        label_scores[label_idx].append(pred_label["score"])

        # Compute the final scores for each label by averaging over all chunks
        final_scores = [
            sum(lst) / len(lst) if len(lst) > 0 else 0 for lst in label_scores
        ]

        # Add the final scores to the corresponding lists
        for label, score, lst in zip(labels, final_scores, lists):
            lst.append(score)

    # Add the final scores for each label as columns to the input DataFrame
    for lsts, label in zip(lists, labels):
        df.insert(len(df.columns), label, lsts)


    # 2. Predict sentiment and subjectivity using FLAIR and TextBlob respectively
    df = flair_x_textblob(df)

    return df
