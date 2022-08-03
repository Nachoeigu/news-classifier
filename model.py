import nltk
from unidecode import unidecode
from nltk.corpus import stopwords
import re
from constants import MORE_STOPWORDS
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import time
from sklearn.metrics import accuracy_score
import numpy as np
import pickle


class NLPClassifier:

    def __init__(self, data):
        self.df = data

    def __generating_stopwords_in_spanish(self):
        self.common_words = []
        for word in stopwords.words('spanish'):
            word = unidecode(re.sub('[\"\'\,\.\:\?\¡\!\¿\d\-\;\|]','',word.lower()))
            self.common_words.append(word)
            
    def __removing_stopwords(self, text):
        text = unidecode(re.sub('[\"\'\,\.\:\?\¡\!\¿\d\-\;\|\“|\”]','',text.lower()))
        
        text = re.sub("\s{2,}", " ", text).split(' ')
        adjusted_text = []
        for word in text:
            if word in MORE_STOPWORDS:
                continue
            else:
                adjusted_text.append(word)
        
        new_sentence = ''
        for word in adjusted_text:
            if word in self.common_words:
                pass
            else:
                new_sentence += ' ' + word
        return new_sentence.strip()

    def preprocessing(self):
        #We drop some nulls values
        self.df = self.df.dropna()
        self.df = self.df[self.df['titles'] != ""]  

        self.df['content'] = self.df['content'].apply(self.__removing_stopwords)
        self.df['titles'] = self.df['titles'].apply(self.__removing_stopwords)
  
        #We put the title and description in one variable
        self.df['text'] = self.df['titles'] + ' ' + self.df['content']
        self.df.drop(columns = ['titles','content'], inplace = True)

        self.transformer = TfidfTransformer(smooth_idf=False) 
        self.count_vectorizer = CountVectorizer(ngram_range=(1,2), max_features = 4000)

    def modelling(self):
        i = time.time()
        X_train, X_test, y_train, y_test = train_test_split(self.df['text'], self.df['labels'], test_size = 0.4, random_state = 20022)

        X_train_transformed =  self.count_vectorizer.fit_transform(X_train.values)
        X_train_transformed = self.transformer.fit_transform(X_train_transformed)

        X_test_transformed = self.count_vectorizer.transform(X_test)
        X_test_transformed = self.transformer.transform(X_test_transformed)

        self.rf = RandomForestClassifier(n_estimators = 150)
        self.rf.fit(X_train_transformed, y_train)

        predictions = self.rf.predict(X_test_transformed)
        print("The modelling phase lasts: ", time.time() - i, " secs.")
        print("The accuracy of the model is: ", round(accuracy_score(y_test, predictions), 3) * 100, '%')

    def predict(self, text:str):
        input_data = np.array([text])
        input_data = self.count_vectorizer.transform(input_data)
        input_data = self.transformer.transform(input_data)

        print("The category of this article is: ", self.rf.predict(input_data)[0])

    def save_model(self):
        pickle.dump(self.rf, open("model.sav", 'wb'))
        
    def load_model(self):
        loaded_model = pickle.load(open("model.sav", 'rb'))
        self.rf = loaded_model
