import streamlit as st
from keybert import KeyBERT
from textblob import TextBlob
import pandas as pd
from nltk.corpus import stopwords
#import texthero as hero
stop = stopwords.words('english')
pd.set_option('precision', 0)
#from sklearn.feature_extraction.text import TfidfVectorizer

@st.cache()
def keybert_extractor(text, min=1, max=5):
    """
    Uses KeyBERT to extract the top n keywords from a text
    Arguments: text (str)
    Returns: list of keywords (list)
    """
    keywords = bert.extract_keywords(text, keyphrase_ngram_range=(min, max), stop_words="english", top_n=num_keywords)
    results = []
    for scored_keywords in keywords:
        for keyword in scored_keywords:
            if isinstance(keyword, str):
                results.append(keyword)
    return results

def textblob_nouns(text):
    blob = TextBlob(text)

    return blob.noun_phrases#, blob.ngrams(n=1), blob.ngrams(n=2), blob.ngrams(n=3)


def textblob_ngrams(text,ngram=1):
    blob = TextBlob(text)
    result = blob.ngrams(n=ngram)
    result_str = " ".join([gram[0] for gram in result if gram[0] not in (stop)])

    return result_str

bert = KeyBERT()
def keybert_extractor(text, min=1, max=5,num_keywords = 20):
    """
    Uses KeyBERT to extract the top n keywords from a text
    Arguments: text (str)
    Returns: list of keywords (list)
    """
    keywords = bert.extract_keywords(text, keyphrase_ngram_range=(min, max), stop_words="english", top_n=num_keywords)
    results = []
    for scored_keywords in keywords:
        for keyword in scored_keywords:
            if isinstance(keyword, str):
                results.append(keyword)
    return results

def get_gram_after_function(list_):

    words, _ = map(list, zip(*list_))
    #words
    return words

st.header('Use keyword extractor to find most common keywords for each year')

if "df_working" not in st.session_state:
    st.write('Please upload a json file in previous page before proceeding with Berttopic modelling')
else:
    df_working = st.session_state['df_working']
    bert = KeyBERT()
    num_keywords = 20

    #st.write(df_working)

    if 'df_working_keywords' not in st.session_state:
        #st.write('adding session state 1')
        st.session_state.df_working_keywords = False

        #if 'textblob_nouns' not in df_working.columns:
        with st.spinner(' Creating unigrams'):

            df_working['textblob_nouns'] = df_working.apply(lambda row : textblob_nouns(row['Data']), axis=1)

        with st.spinner('keywords using KeyBert'):

            df_working['keywords_bert'] = bert.extract_keywords(df_working['Data'], keyphrase_ngram_range=(1, 1), stop_words="english", top_n=20)
            df_working['keywords_bert'] = df_working.apply(lambda row : get_gram_after_function(row['keywords_bert']), axis=1)
            df_working['keywords_bert'] = df_working.apply(lambda row : ' '.join(row['keywords_bert']), axis=1)


        st.write('generated keywords')
        st.session_state.df_working_keywords = df_working
        st.write(df_working)


    else:
        df_working = st.session_state.df_working_keywords

        output = pd.Series(' '.join(df_working['keywords_bert']).lower().split(), name = 'occurences').value_counts()[:100]

        st.subheader('Most frequent words across dataframe (Title and Text)')
        st.table(output)

        keyword_year_df = pd.DataFrame()

        # Get current list of columns
        proper_cols_ = list(set(df_working.Year.values.tolist()))
        proper_cols_ = sorted(proper_cols_)

        keyword_year_df = pd.DataFrame()
        for year in proper_cols_:
            if year == str(2023):
                continue
            #st.write('year', year)

            temp_year_df = df_working[df_working['Year'] == str(year)]
            temp_output = pd.Series(' '.join(temp_year_df['keywords_bert']).lower().split(), name = str(year)).value_counts()[:100]
            keyword_year_df = pd.concat([keyword_year_df,temp_output],axis = 1)

        keyword_year_df = keyword_year_df.fillna(0)
        keyword_year_df = keyword_year_df.astype(int)

        st.subheader('Keyword occurences per year')
        st.table(keyword_year_df)

        if 'berttopic_model_df' not in st.session_state:
            st.write('Please run Bert topic to generate topic ids for each document before proceeding')
        else:
            berttopic_model_df = st.session_state.berttopic_model_df

            topic_list = list(set(berttopic_model_df.bert_topic_id.values.tolist()))
            topic_list = sorted(topic_list)

            topic_keyword_year_df = pd.DataFrame()

            final_topic_and_bert_df = df_working.merge(berttopic_model_df)#,df_working)


            st.subheader('Find occurences of keywords by topic id over time')
            if 'topic_slider_val' not in st.session_state:
                st.session_state.topic_slider_val = False

            topic_slider_val = st.select_slider('Choose a topic id ', options = sorted(berttopic_model_df['bert_topic_id'].unique()))
            st.session_state.topic_slider_val = topic_slider_val

            #st.write('topic_slider_val', topic_slider_val)

            for year in proper_cols_:
                if year == str(2023):
                    continue
                #st.write('year', year)

                temp_year_df_topic = final_topic_and_bert_df[(final_topic_and_bert_df['Year'] == str(year)) & (final_topic_and_bert_df['bert_topic_id'] == (topic_slider_val))]
                #st.write('temp_year_df_topic', temp_year_df_topic)
                temp_year_df_topic = pd.Series(' '.join(temp_year_df_topic['keywords_bert']).lower().split(), name = str(year)).value_counts()
                topic_keyword_year_df = pd.concat([topic_keyword_year_df,temp_year_df_topic],axis = 1)

            #st.write('Keyword frequency per year and topic')
                #st.write('year',year),
            st.write(f" Showing top keywords for topic id {topic_slider_val}")
            #topic_keyword_year_df
            topic_keyword_year_df = topic_keyword_year_df.fillna(0)
            topic_keyword_year_df = topic_keyword_year_df.astype(int)

            st.dataframe(topic_keyword_year_df.fillna(0))
