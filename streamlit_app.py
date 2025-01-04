import streamlit as st
from afinn import Afinn  # AFINN sentiment lexicon
import re  # For handling phrases

# Initialize AFINN lexicon
afinn = Afinn()

# Function to map sentiment scores to sentiment statements
def get_sentiment_statement(score):
    if score >= 3:
        return "Very Positive"
    elif 1 < score <= 2:
        return "Positive"
    elif 0 < score <= 1:
        return "Slightly Positive"
    elif score == 0:
        return "Neutral"
    elif -1 <= score < 0:
        return "Slightly Negative"
    elif -2 <= score < -1:
        return "Negative"
    elif score <= -3:
        return "Very Negative"

# For modifiers and negations
modifiers = {
    "very": 1,
    "extremely": 2,
    "absolutely": 2,
    "totally": 2,
    "slightly": -0.5,
}

negations = {"not", "no", "never", "hardly"}

# Sentiment analysis function
def analyze_sentiment(input_text):
    # Tokenize text into words
    tokens = re.findall(r'\w+|[^\w\s]', input_text)
    word_scores = []
    overall_score = 0

    # Process tokens with negation and modifier handling
    i = 0
    while i < len(tokens):
        token = tokens[i].lower()
        score = 0

        if token in negations:
            word_scores.append((tokens[i], 0))  # Negation words themselves are neutral
            if i + 1 < len(tokens):
                next_token = tokens[i + 1].lower()
                next_score = afinn.score(next_token)
                if next_score != 0:
                    score = -next_score  # Reverse sentiment of the next word
                    word_scores.append((tokens[i + 1], score))  # Add next word with modified score
                    i += 1
        elif token in modifiers:
            word_scores.append((tokens[i], 0))  # Modifier words themselves are neutral
            if i + 1 < len(tokens):
                next_token = tokens[i + 1].lower()
                next_score = afinn.score(next_token)
                if next_score != 0:
                    score = next_score + modifiers[token]
                    word_scores.append((tokens[i + 1], score))  # Add next word with modified score
                    i += 1
        else:
            score = afinn.score(token)
            word_scores.append((tokens[i], score))  # Normal words with their sentiment score

        overall_score += score
        i += 1

    sentiment_statement = get_sentiment_statement(overall_score)
    return word_scores, overall_score, sentiment_statement

# Streamlit Application
st.title("Sentiment Analysis Tool")

# Input Field
st.subheader("Enter Text for Sentiment Analysis")
input_text = st.text_area("Text Input", "", height=150)

# Analyze Button
if st.button("Analyze Sentiment"):
    if not input_text.strip():
        st.error("Please enter some text.")
    else:
        # Analyze sentiment
        word_scores, overall_score, sentiment_statement = analyze_sentiment(input_text)

        # Display Tokens with Color Coding
        st.subheader("Word Sentiment Scores")
        colored_text = ""
        for token, score in word_scores:
            if score > 0:
                color = f"rgb(0, {min(255, int(score * 50))}, 0)"  # Green shades
            elif score < 0:
                color = f"rgb({min(255, int(abs(score) * 50))}, 0, 0)"  # Red shades
            else:
                color = "white"
            colored_text += f"<span style='color:{color}; font-weight:bold;'>{token}</span> "

        # Render Colored Text using HTML
        st.markdown(colored_text, unsafe_allow_html=True)

        # Display Overall Sentiment
        st.subheader("Overall Sentiment")
        st.write(f"**Sentiment:** {sentiment_statement}")
        # st.write(f"**Score:** {overall_score}")
