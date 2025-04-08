# https: // www.theguardian.com/uk-news/2025/apr/07/johnson-and -sunak-may-be-asked-to-give-evidence-at-asylum-centre-inquiry
from textblob import TextBlob
import nltk
import spacy
import yake
from keybert import KeyBERT
from rake_nltk import Rake

from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt_tab')


with open("initial_article.txt", "r") as file:
    content = file.read()

sia = SentimentIntensityAnalyzer()
sentiment = sia.polarity_scores(content)

print("Sentiment Scores:", sentiment)

blob = TextBlob(content)
print("Subjectivity:", blob.sentiment.subjectivity)
print("Polarity:", blob.sentiment.polarity)

print("\n \n \n below is keybert \n \n \n")


kw_model = KeyBERT()
keywords = kw_model.extract_keywords(
    content, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=10)

print("Top keywords / topic candidates:")
for kw, score in keywords:
    print(f"{kw} ({score:.2f})")

print("\n \n \n below is rake \n \n \n")

r = Rake()
r.extract_keywords_from_text(content)
keywords = r.get_ranked_phrases()
print(keywords[:10])

print("\n \n \n below is yake \n \n \n")
kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=10)
keywords = kw_extractor.extract_keywords(content)
print([kw for kw, score in keywords])

print("\n \n \n below is spacy \n \n \n")


nlp = spacy.load("en_core_web_sm")
sid = SentimentIntensityAnalyzer()

doc = nlp(content)
for ent in doc.ents:
    sentence = ent.sent.text
    sentiment = sid.polarity_scores(sentence)
    print(f"{ent.text} ({ent.label_}): {sentiment}")