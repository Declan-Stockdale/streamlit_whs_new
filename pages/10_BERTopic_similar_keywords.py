import streamlit as st
from bertopic import BERTopic
from umap import UMAP
import pandas as pd

st.header('Search through bertopic model for topics with similar words')
st.write('The result of this page is a table of topics and keywords which are most similar to the input keyword. ')

#for keys in st.session_state.keys():
    #st.write(keys)

st.write("")
st.write("")
st.write("")
# requires dataframe from json and compelx model to proceed
if "df_working" not in st.session_state:
    st.subheader('Please upload a json file in the previous page before proceeding with BERTopic model')

if 'bertopic_model' not in st.session_state: # could change to elif?
    st.subheader('Please run the previous page to generate a model')

else:
    # bot json and bertopic model exist in memory

    # load model from memory
    bertopic_model = st.session_state.bertopic_model

    # set placeholder for memory
    if 'keywords_bert' not in st.session_state:
        st.session_state.keywords_bert = False

    # keyword input
    keywords_bert = st.text_input('Find documents with keywords')#.to_list()
    proceed_button_bert =  st.button('Search for documents containing keyword')

    if proceed_button_bert: # button was clicked

    # empty df
        associated_topics_keyword = pd.DataFrame()

        # loop over topics
        for topic_id in bertopic_model.find_topics(keywords_bert)[0]:
            topic_word_list = []

            # get similar words
            word = bertopic_model.get_topic(topic=topic_id)
            # loop over similar words
            for word_val in word:
                topic_word_list.append(word_val[0])

            # Convert to series
            topic_word_df = pd.Series(topic_word_list,name = topic_id)
            # concat to dataframe
            associated_topics_keyword = pd.concat([associated_topics_keyword,topic_word_df],axis = 1)

        st.write('Table of topics and associated words for a given keyword')
        st.write(associated_topics_keyword)

        # download functionality
        st.download_button(
            label="Download Top 10 texts per topic",
            data=associated_topics_keyword.to_csv(),
            file_name=str(keywords_bert)+'_keyword_realted_topics.csv',
            mime='text/csv'
        )
