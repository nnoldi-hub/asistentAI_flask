
import json
import random
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

with open("intents.json", "r", encoding="utf-8") as file:
    data = json.load(file)

training_sentences = []
training_labels = []
labels = []
responses = {}

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        training_sentences.append(pattern)
        training_labels.append(intent["tag"])
    responses[intent["tag"]] = intent["responses"]
    if intent["tag"] not in labels:
        labels.append(intent["tag"])

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(training_sentences)
y = training_labels

model = MultinomialNB()
model.fit(X, y)

with open("model.pkl", "wb") as file:
    pickle.dump(model, file)

with open("vectorizer.pkl", "wb") as file:
    pickle.dump(vectorizer, file)

with open("responses.pkl", "wb") as file:
    pickle.dump(responses, file)
