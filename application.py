import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
from methodes import *  


knowledge_base_path = "data.json"  
knowledge_base = load_knowledge_base(knowledge_base_path)


def main():
    st.set_page_config(layout="wide")
    st.sidebar.title("Data Quality Analysis")
    uploaded_file = st.sidebar.file_uploader("Upload Dataset", type=["csv", "xlsx"], key='file_uploader')

    if uploaded_file is not None:
        if 'data' not in st.session_state:
            try:
                if uploaded_file.name.endswith(".csv"):
                    csv_file = StringIO(uploaded_file.getvalue().decode("utf-8"))
                    df = pd.read_csv(csv_file)
                elif uploaded_file.name.endswith(".xlsx"):
                    csv_file = StringIO(uploaded_file.getvalue().decode("utf-8"))
                    df = pd.read_excel(uploaded_file)
                st.session_state['data'] = df
                st.sidebar.success("Dataset uploaded successfully!")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
        else:
            df = st.session_state['data'].copy()

        ######################################################
     
        if st.sidebar.button("Data Info", key='data_info_btn'):
            reset_all_flags()
            st.session_state['show_data_info'] = True

        if 'show_data_info' in st.session_state and st.session_state['show_data_info']:
            reset_all_flags()
            st.header("Data Info")
            df_info = display_info(df)
            st.text(df_info)

        ######################################################
       
        if st.sidebar.button("Describe Data", key='describe_data_btn'):
            reset_all_flags()
            st.session_state['describe_data'] = True

        if 'describe_data' in st.session_state and st.session_state['describe_data']:
            reset_all_flags()
            st.header("Data Description")
            st.table(describe_data(df))

        ######################################################
         
        if st.sidebar.button("Handle Missing Values", key='missing_values_btn'):
           
            reset_all_flags()
            st.session_state['missing_values_run'] = True
            
        if 'missing_values_run' in st.session_state and st.session_state['missing_values_run']:
           
            st.header("Missing Values Handling")
            
            col1, col2 = st.columns(2)
            with col1:
                column_for_missing = st.selectbox(
                    "Select Column for Missing Value Handling", df.select_dtypes(include=['float64', 'int64']).columns,
                    key="missing_col"
                )

            with col2:
                missing_method = st.selectbox(
                    "Select Missing Value Handling Method",
                    ['mean', 'median', 'mode', 'drop'],
                    key="missing_method"
                )
            
            missing_count = missing_value_analysis(df, column_for_missing)
            
            if missing_count > 0:
                st.session_state['df_before_missing'] = df.copy()

                st.session_state['df_after_missing'] = handle_missing_values(
                    df.copy(), column_for_missing, missing_method
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.header("Data Before Handling Missing Values")
                    st.write(f"Number of missing values before handling: {missing_count}")
                    st.write(st.session_state['df_before_missing'])
                    
                    if st.checkbox("Show heatmap Before", key="heat_before"):
                            fig, ax = plt.subplots()
                            sns.heatmap(df.isnull(), cmap="viridis", cbar=True, ax=ax)
                            plt.title(f"heatmap of {column_for_missing} (Before)")
                            st.pyplot(fig)

                with col2:
                    st.header("Data After Handling Missing Values")
                    st.write(f"Number of missing values after handling: {st.session_state['df_after_missing'][column_for_missing].isnull().sum()}")
                    st.write(st.session_state['df_after_missing'])
                    if st.checkbox("Show heatmap after", key="heat_after"):
                          fig, ax = plt.subplots(figsize=(10, 6))
                          sns.heatmap(st.session_state['df_after_missing'].isnull(), cmap="viridis", cbar=True, ax=ax)
                          plt.title(f"heatmap of {column_for_missing} (after)")
                          st.pyplot(fig)
                
                if st.button("OK"):
                    df = st.session_state['df_after_missing']
                    st.session_state['data'] = df
                    st.success("Changes applied to the dataset.")
            
            else:
                st.info(f"No missing values detected in the column {column_for_missing}.")
        
        ######################################################
       
        if st.sidebar.button("Handle Duplicates", key='duplicates_btn'):
            
            st.session_state['missing_values_run'] = False
            reset_all_flags()
            st.session_state['duplicates_run'] = True

        if 'duplicates_run' in st.session_state and st.session_state['duplicates_run']:
            st.header("Duplicate Values Handling")
    
            col1, col2 = st.columns(2)
            with col1:
                column_for_duplicates = st.selectbox(
                    "Select Column for Duplicate Handling", df.select_dtypes(include=['float64', 'int64', 'object']).columns,
                    key="duplicate_col"
                )
    
            with col2:
                duplicate_method = st.selectbox(
                    "Select Duplicate Handling Method",
                    ['keep_first', 'keep_last', 'drop_duplicates', 'drop_all'],
                    key="duplicate_method"
                )

            # Analyze duplicates in the entire DataFrame
            duplicate_count = duplicate_value_analysis(df , column_for_duplicates)

            if duplicate_count > 0:
                st.session_state['df_before_duplicates'] = df.copy()
                st.session_state['df_after_duplicates'] = handle_duplicates(
                    df.copy(), column_for_duplicates, duplicate_method
                )
                # Handle duplicates based on selected method
                
                col1, col2 = st.columns(2)
                with col1:
                    st.header("Data Before Handling Duplicates")
                    st.write(f"Number of duplicate rows before handling: {duplicate_count}")
                    st.write(st.session_state['df_before_duplicates'])

                    

                with col2:
                    st.header("Data After Handling Duplicates")
                    remaining_duplicates = st.session_state['df_after_duplicates'].duplicated().sum()
                    st.write(f"Number of duplicate rows after handling: {remaining_duplicates}")
                    st.write(st.session_state['df_after_duplicates'])


                if st.button("OK", key="ok_duplicates"):
                    df = st.session_state['df_after_duplicates']
                    st.session_state['data'] = df
                    st.success("Changes applied to the dataset.")

            else:
                st.info(f"No duplicate rows detected in the column {column_for_duplicates}.")
        
        ######################################################
        
        if st.sidebar.button("Handle Outlier", key='outlier_analysis_btn'):
            
            st.session_state['missing_values_run'] = False
            reset_all_flags()
            # st.session_state.clear()
            st.session_state['outlier_analysis_run'] = True

        if 'outlier_analysis_run' in st.session_state and st.session_state['outlier_analysis_run']:
           
            st.header("Outliers Handling")

            col1, col2 = st.columns(2)

            with col1:
                column_for_outlier = st.selectbox(
                    "Select Column for Outlier Analysis",
                    df.select_dtypes(include=['float64', 'int64']).columns,
                    key="outlier_col"
                )

            with col2:
                outlier_method = st.selectbox(
                    "Select Outlier Handling Method",
                    ['', 'clip', 'drop'],
                    key="outlier_method"
                )

            if outlier_method == '':
                st.warning("Please select an outlier handling method (clip or drop).")
            else:
                lower_bound, upper_bound = outlier_analysis(df, column_for_outlier)

                if lower_bound is not None and upper_bound is not None:
                    st.session_state['df_before_outliers'] = df.copy()

                    before_outliers = df[(df[column_for_outlier] < lower_bound) | (df[column_for_outlier] > upper_bound)]
                    num_before_outliers = before_outliers.shape[0]

                    st.session_state['df_after_outliers'] = handle_outliers(
                        df.copy(), column_for_outlier, lower_bound, upper_bound, outlier_method
                    )

                    after_outliers = st.session_state['df_after_outliers'][ 
                        (st.session_state['df_after_outliers'][column_for_outlier] < lower_bound) |
                        (st.session_state['df_after_outliers'][column_for_outlier] > upper_bound)
                    ]
                    num_after_outliers = after_outliers.shape[0]

                    col1, col2 = st.columns(2)
                    with col1:
                        st.header("Data Before Handling Outliers")
                        st.write(f"Number of outliers before handling: {num_before_outliers}")
                        st.write(st.session_state['df_before_outliers'])
                        if st.checkbox("Show Boxplot Before", key="boxplot_before"):
                            fig, ax = plt.subplots()
                            sns.boxplot(x=st.session_state['df_before_outliers'][column_for_outlier], ax=ax)
                            plt.title(f"Box Plot of {column_for_outlier} (Before)")
                            st.pyplot(fig)

                    with col2:
                        st.header("Data After Handling Outliers")
                        st.write(f"Number of outliers after handling: {num_after_outliers}")
                        st.write(st.session_state['df_after_outliers'])
                        if st.checkbox("Show Boxplot After", key="boxplot_after"):
                            fig, ax = plt.subplots()
                            sns.boxplot(x=st.session_state['df_after_outliers'][column_for_outlier], ax=ax)
                            plt.title(f"Box Plot of {column_for_outlier} (After)")
                            st.pyplot(fig)

                    if st.button("OK"):
                        df = st.session_state['df_after_outliers']
                        st.session_state['data'] = df
                        st.success("Changes applied to the dataset.")

        ######################################################
       
        if st.sidebar.button("Download dataset", key='download_btn'):
            st.session_state['missing_values_run'] = False
            reset_all_flags()
            download_dataset(df)
        
            ######################################################
       
        if st.sidebar.button("Knowledge Base (RAG)", key='rag_btn'):
            
            st.session_state['missing_values_run'] = False
            reset_all_flags()
            st.session_state['rag_run'] = True

        if 'rag_run' in st.session_state and st.session_state['rag_run']:
            st.header("Knowledge Base (RAG)")

           
            topic = st.selectbox("Select the topic", knowledge_base.keys(), key="rag_topic")

            if topic:
               
                question = st.text_input(
                    "Write the question", 
                    # [qa["question"] for qa in knowledge_base[topic]],
                    key="rag_question"
                )

                if st.button("Get Answer", key="get_answer_btn"):
                    answer = get_answer_from_knowledge_base(knowledge_base, topic, question)
                    st.write(f"**answer** {answer}")


if __name__ == "__main__":
    main()
