import pickle
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, confusion_matrix
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.svm import LinearSVC
from scipy.stats import randint
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout
from keras.optimizers import Adam

df = pd.read_csv("blogtext.csv", nrows=20000)
print(df.shape)

"""# **EDA**"""

df.head()

df.isnull().sum()

df.describe()

df["topic"].value_counts()

# Calculate the length of each text in terms of characters
df['text_length'] = df['text'].apply(len)

# Plot a histogram of text lengths
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='text_length', bins=50, kde=True)
plt.title('Distribution of Text Lengths')
plt.xlabel('Text Length (Characters)')
plt.ylabel('Frequency')
plt.show()

#Word Count Distribution by Topic:

plt.figure(figsize=(12, 8))
sns.boxplot(data=df, y='topic', x='text_length')
plt.title('Word Count Distribution by Topic')
plt.ylabel('Topic')
plt.xlabel('Text Length (Characters)')
plt.show()

"""# **Pre-processing**"""

# Lowercasing
df['processed_text'] = df['text'].apply(lambda x: x.lower())
df['processed_text'].head()

# Remove special characters and numbers
df['processed_text'] = df['processed_text'].apply(lambda x: re.sub(r"[^a-zA-Z]", " ", x))
df['processed_text'].head()

# Tokenization and remove stop words
stop_words = set(stopwords.words("english"))
df['processed_text'] = df['processed_text'].apply(lambda x: ' '.join([word for word in word_tokenize(x) if word not in stop_words]))
df['processed_text'].head()

# Lemmatization
lemmatizer = WordNetLemmatizer()
df['processed_text'] = df['processed_text'].apply(lambda x: ' '.join([lemmatizer.lemmatize(word) for word in word_tokenize(x)]))
df.head()

# Plot the top N lemmas
from collections import Counter
N = 20  # Change this to the desired number of top lemmas
all_lemmas = ' '.join(df['processed_text']).split()
lemma_counts = Counter(all_lemmas)
top_lemmas = lemma_counts.most_common(N)
top_lemmas, freq = zip(*top_lemmas)
plt.figure(figsize=(12, 6))
sns.barplot(x=list(top_lemmas), y=list(freq))
plt.title(f'Top {N} Lemmas after Preprocessing')
plt.xlabel('Lemma')
plt.ylabel('Frequency')
plt.xticks(rotation=45)
plt.show()

# Add the import statement for WordCloud
from wordcloud import WordCloud

all_text = ' '.join(df['processed_text'])
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)

# Plot the word cloud
plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.title('Word Cloud of Processed Text')
plt.axis('off')
plt.show()

# Create a new dataframe with two columns
df2 = df[["sign", "processed_text"]]
df2.head()

print(df2['sign'].unique())

from sklearn.preprocessing import LabelEncoder
# Create a LabelEncoder object
label_encoder = LabelEncoder()
# Fit the LabelEncoder on the 'zodiac_sign' column to learn the mapping
label_encoder.fit(df2['sign'])
# Transform the zodiac sign labels to encoded numerical labels
df2['sign_id'] = label_encoder.transform(df2['sign'])

df2.head()

# Plot the occurrence of each zodiac sign using seaborn
plt.figure(figsize=(10, 6))
sns.countplot(data=df2, x='sign', order=df2['sign'].value_counts().index)
plt.xlabel('Zodiac Sign')
plt.ylabel('Frequency')
plt.title('Occurrence of Zodiac Signs')
plt.xticks(rotation=45, ha='right')
plt.show()



# Define the TF-IDF vectorizer
tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, ngram_range=(1, 2), stop_words="english")

# Transform the text data and labels using TF-IDF vectorizer
X_tfidf = tfidf.fit_transform(df2['processed_text'])
labels = df2['sign_id']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, labels, test_size=0.2, random_state=42)

# Train a Random Forest classifier for Zodiac Sign Prediction
rf_classifier_zodiac = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier_zodiac.fit(X_train, y_train)

# ... (Rest of the code remains the same)


'''
# Create a TF-IDF Vectorizer
tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, ngram_range=(1,2), stop_words="english")
features = tfidf.fit_transform(df.text).toarray()
labels = df2['sign_id']
features.shape

# Define the number of most correlated terms to display
N = 2
sign_id_df = df2[["sign", "sign_id"]].drop_duplicates()
sign_to_id = dict(sign_id_df.values)

sign_id_df.head(12)

from sklearn.feature_selection import chi2

# Iterate through each zodiac sign and its corresponding ID
for sign, sign_id in sorted(sign_to_id.items()):
    # Calculate chi-squared test between features and the current sign's labels
    features_chi2 = chi2(features, labels == sign_id)

    # Sort feature indices based on chi-squared test statistics
    indices = np.argsort(features_chi2[0])

    # Get the feature names (terms) in sorted order based on chi-squared test
    feature_names = np.array(tfidf.get_feature_names_out())[indices]

    # Filter out unigrams and bigrams from the sorted feature names
    unigrams = [v for v in feature_names if len(v.split(" ")) == 1]
    bigrams = [v for v in feature_names if len(v.split(" ")) == 2]

    # Print the most correlated unigrams and bigrams for the current zodiac sign
    print("n--> %s:" %(sign))
    print("  * Most Correlated Unigrams are: %s" %(", ".join(unigrams[-N:])))
    print("  * Most Correlated Bigrams are: %s" %(", ".join(bigrams[-N:])))

"""# **Random Forest Classifier**"""

# Feature Extraction: Using TF-IDF
X_tfidf = tfidf.fit_transform(df2['processed_text'])

y = df2["sign"] # Target or the labels we want to predict (i.e. the 12 different zodiac signs)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# Train a Random Forest classifier for Zodiac Sign Prediction
rf_classifier_zodiac = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier_zodiac.fit(X_train, y_train)
'''

# Make predictions on the test set for Zodiac Sign Prediction
y_pred = rf_classifier_zodiac.predict(X_test)

# Calculate and print accuracy and classification report for Zodiac Sign Prediction
accuracy_rf = accuracy_score(y_test, y_pred)
print("Accuracy for Zodiac Sign Prediction:", accuracy_rf)

print("\nClassification Report for Zodiac Sign Prediction:")
print(classification_report(y_test, y_pred))

conf_mat = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots()
sns.heatmap(conf_mat, annot=True, cmap="Blues", fmt='d', xticklabels=sign_id_df.sign.values, yticklabels=sign_id_df.sign.values)
plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.title("CONFUSION MATRIX - RandomForestClassifier", size=12)

#bimz- add
import matplotlib.pyplot as plt

unique_zodiacs = df2["sign"].unique()
accuracy_by_class = [accuracy_score(y_test[y_test == sign], y_pred[y_test == sign]) for sign in unique_zodiacs]

plt.figure(figsize=(10, 6))
plt.bar(unique_zodiacs, accuracy_by_class)
plt.xlabel("Zodiac Sign")
plt.ylabel("Accuracy")
plt.title("Accuracy by Zodiac Sign")
plt.xticks(rotation=45)
plt.show()

"""# **LinearSVC**

"""

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

from sklearn.svm import LinearSVC

# Create and train the LinearSVC model
svc_classifier = LinearSVC()
svc_classifier.fit(X_train, y_train)

# Make predictions on the test set
y_pred = svc_classifier.predict(X_test)

from sklearn.metrics import accuracy_score, classification_report

# Calculate accuracy
accuracy_linsvc = accuracy_score(y_test, y_pred)
print("Accuracy for Zodiac Sign Prediction using LinearSVC:", accuracy_linsvc )

# Print the classification report
print("\nClassification Report for Zodiac Sign Prediction:")
print(classification_report(y_test, y_pred))

#bimz-add
from sklearn.metrics import classification_report

# Get the classification report
report = classification_report(y_test, y_pred, target_names=sign_id_df.sign.values, output_dict=True)

# Extract precision, recall, and F1-score for each class
class_names = list(report.keys())[:-3]  # Exclude 'micro avg', 'macro avg', 'weighted avg'
precision_values = [report[class_name]['precision'] for class_name in class_names]
recall_values = [report[class_name]['recall'] for class_name in class_names]
f1_values = [report[class_name]['f1-score'] for class_name in class_names]

# Plot the class-wise metrics
plt.figure(figsize=(12, 6))
plt.barh(class_names, precision_values, color='b', label='Precision')
plt.barh(class_names, recall_values, color='g', label='Recall')
plt.barh(class_names, f1_values, color='r', label='F1-Score')
plt.xlabel('Score')
plt.title('Class-wise Precision, Recall, and F1-Score')
plt.legend()
plt.show()

conf_mat = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots()
sns.heatmap(conf_mat, annot=True, cmap="Blues", fmt='d', xticklabels=sign_id_df.sign.values, yticklabels=sign_id_df.sign.values)
plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.title("CONFUSION MATRIX - LinearSVC", size=12)

"""#**LinearSVC Model Tunning**

We can start with Random Search to quickly narrow down the hyperparameter space and then refine our search using Grid Search around the promising regions.

**Random Search**
"""

# Define the parameter distribution to sample from
param_dist = {
    'C': [0.01, 0.1, 1, 10],         # Regularization parameter
    'loss': ['hinge', 'squared_hinge'],  # Loss function
    'max_iter': randint(100, 500)    # Maximum number of iterations
}

# Create the RandomizedSearchCV object
random_search = RandomizedSearchCV(svc_classifier, param_distributions=param_dist, n_iter=10, cv=5, n_jobs=-1)

# Perform the random search
random_search.fit(X_train, y_train)

# Print the best hyperparameters and corresponding accuracy
print("Best Hyperparameters:", random_search.best_params_)
print("Best Accuracy:", random_search.best_score_)

"""**Grid Search**"""

# Define the parameter grid to search based on the best hyperparameters from Random Search
param_grid = {
    'C': [0.8, 0.9, 1, 1.1, 1.2],         # Narrower range around the best 'C' value
    'loss': ['hinge'],                    # Use the best 'loss' value
    'max_iter': [300, 350, 400]            # Narrower range around the best 'max_iter' value
}

# Create the GridSearchCV object
grid_search = GridSearchCV(svc_classifier, param_grid, cv=5, n_jobs=-1)

# Perform the grid search
grid_search.fit(X_train, y_train)

# Print the best hyperparameters and corresponding accuracy
print("Best Hyperparameters:", grid_search.best_params_)
print("Best Accuracy:", grid_search.best_score_)

"""**Training LinearSVC using best Hyperparameters**"""



# Create a LinearSVC model with the best hyperparameters from Grid Search
best_svc_model = LinearSVC(C=1.2, loss='hinge', max_iter=300)

# Train the model on the entire training dataset
best_svc_model.fit(X_train, y_train)

# Make predictions on the test data
y_pred = best_svc_model.predict(X_test)

# Calculate accuracy and other metrics
accuracy_tune = accuracy_score(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred)

print("Accuracy:", accuracy_tune)

print("Classification Report:\n", classification_rep)

# Create a confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred)

# Plot the confusion matrix using seaborn
plt.figure(figsize=(10, 8))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=best_svc_model.classes_, yticklabels=best_svc_model.classes_)
plt.title("Confusion Matrix")
plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.show()

# List of model names
model_names = ['Random Forest', 'LinearSVC', 'Tuned LinearSVC']

# List of pre-calculated accuracy values
accuracies = [accuracy_rf, accuracy_linsvc, accuracy_tune]

# Plotting
plt.figure(figsize=(10, 6))
bars = plt.bar(model_names, accuracies, color=['blue', 'orange', 'green'])
plt.xlabel('Models')
plt.ylabel('Accuracy Score')
plt.title('Model Comparison - Accuracy')
plt.ylim(0.0, 1.0)  # Set y-axis range

# Adding accuracy values as labels on top of bars
for bar, accuracy in zip(bars, accuracies):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f'{accuracy:.3f}', ha='center', color='black')

plt.show()


with open("fitted_tfidf_vectorizer.pkl", "wb") as vectorizer_file:
    pickle.dump(tfidf, vectorizer_file)
    
with open("best_svc_model.pkl", "wb") as model_file:
    pickle.dump(best_svc_model, model_file)