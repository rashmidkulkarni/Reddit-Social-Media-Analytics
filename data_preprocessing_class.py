import pandas as pd
import re
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from nltk import pos_tag

class TextProcessor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.punkt = set(string.punctuation)

    def clean_emojis_special_char(self, text):
        if not isinstance(text, str):
            return ""

        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  
                                   u"\U0001F300-\U0001F5FF"  
                                   u"\U0001F680-\U0001F6FF"  
                                   u"\U0001F700-\U0001F77F"  
                                   u"\U0001F780-\U0001F7FF"  
                                   u"\U0001F800-\U0001F8FF"  
                                   u"\U0001F900-\U0001F9FF"  
                                   u"\U0001FA00-\U0001FA6F"  
                                   u"\U0001FA70-\U0001FAFF"  
                                   u"\U00002702-\U000027B0"  
                                   u"\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text

    def nlp_tasks(self, df, text_column):
        df['text_processed'] = df[text_column].apply(self.clean_emojis_special_char).str.lower()
        df['tokens'] = df['text_processed'].apply(word_tokenize)
        df['tokens_punkt'] = df['tokens'].apply(lambda tokens: [token for token in tokens if token not in self.punkt])
        df['tokens_stop'] = df['tokens'].apply(lambda tokens: [token for token in tokens if token not in self.stop_words])
        df['tokens_stemmed'] = df['tokens_stop'].apply(lambda tokens: [self.stemmer.stem(token) for token in tokens])
        df['text_no_stop'] = df['tokens_stop'].apply(' '.join)
        df['text_stemmed_no_stopped'] = df['tokens_stemmed'].apply(' '.join)
        df['pos_tags'] = df['tokens_stemmed'].apply(pos_tag)
        return df

    def text_preprocessed(self, df, text_column):
        df[text_column] = df[text_column].fillna("")
        df = self.nlp_tasks(df, text_column)
        return df