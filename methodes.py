import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import StringIO
import json
import io

def display_info(df):
    """Prepares DataFrame info for display."""
    buffer = io.StringIO()
    df.info(buf=buffer)
    return buffer.getvalue()
############################################################

def describe_data(df):
    """Generates descriptive statistics for the DataFrame."""
    return df.describe()
#########################################################
def missing_value_analysis(df, column):
    """Analyzes missing values in a specified column."""
    missing_count = df[column].isnull().sum()
    return missing_count

def handle_missing_values(df, column, method='mean'):
    """Handles missing values in a column based on the selected method."""
    if method == 'mean':
        df[column].fillna(df[column].mean(), inplace=True)
        st.success(f"Missing values in {column} have been filled with the mean.")
    elif method == 'median':
        df[column].fillna(df[column].median(), inplace=True)
        st.success(f"Missing values in {column} have been filled with the median.")
    elif method == 'mode':
        df[column].fillna(df[column].mode()[0], inplace=True)
        st.success(f"Missing values in {column} have been filled with the mode.")
    elif method == 'drop':
        df.dropna(subset=[column], inplace=True)
        st.success(f"Rows with missing values in {column} have been removed.")
    else:
        st.error("Invalid method for handling missing values.")

    return df

###########################################################
def duplicate_value_analysis(df, column):
    duplicate_count = df[column].duplicated().sum()
    return duplicate_count

def handle_duplicates(df, column, method='drop'):
    """Handles duplicate values in the DataFrame based on the selected method."""
    if method == 'keep_first':
        df = df.drop_duplicates(subset=column, keep='first')
    elif method == 'keep_last':
        df = df.drop_duplicates(subset=column, keep='last')
    elif method == 'drop_duplicates':
        df = df.drop_duplicates(subset=column, keep=False)
    elif method == 'drop_all':
        df = df.drop_duplicates(subset=column, keep=False)

    # Store the modified DataFrame in session state
    st.session_state['df_after_duplicates'] = df
    
    return df

###########################################################
def outlier_analysis(df, column):
    """Identifies and displays outliers using the IQR method."""
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return lower_bound, upper_bound

def handle_outliers(df, column, lower_bound, upper_bound, method='clip'):
    """Handles outliers based on the selected method."""
    if method == 'clip':
        df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
        st.success(f"Outliers in {column} have been clipped to the defined bounds.")
    elif method == 'drop':
        df.drop(df[(df[column] < lower_bound) | (df[column] > upper_bound)].index, inplace=True)
        st.success(f"Outliers in {column} have been removed.")
    else:
        st.error("Invalid method for handling outliers.")
    
    return df

###########################################################

def download_dataset(df):
    """Downloads the DataFrame as a CSV file."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="downloaded_data.csv">Download CSV</a>'
    st.markdown(href, unsafe_allow_html=True)
###########################################################
def reset_all_flags():
    
    """Resets all conditional display flags."""
    keys_to_reset = [
        'show_data','show_data_info' ,'describe_data', 'missing_analysis_run',
        'missing_values_handled', 'duplicates_run',
        'outlier_analysis_run', 'outliers_handled','rag_run'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
           st.session_state[key] = False
     
        else:
            st.session_state[key] = False

    
            
           ##################################


def load_knowledge_base(file_path):
    """Loads the knowledge base from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_answer_from_knowledge_base(knowledge_base, topic, question):
    """Fetches an answer from the knowledge base for a specific topic and question."""
    for qa in knowledge_base.get(topic, []):
        if qa['question'] == question:
            return qa['answer']
    return "No answer found for the question."
