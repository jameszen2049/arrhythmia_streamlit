import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import seaborn as sns
import requests
from streamlit_lottie import st_lottie
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from sklearn.metrics import accuracy_score, recall_score, classification_report, confusion_matrix, roc_auc_score
import altair as alt 
import networkx as nx
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
#from keras.models import load_model
#import tensorflow as tf

# ---- Page Title with Icon ----
st.set_page_config(page_title='Arrhythmia Classification', page_icon=':anatomical_heart:')

# ---- Load GFX Assets ----

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

ecg_gfx = 'https://lottie.host/37bfe504-9620-477e-ad38-f32dfe93f35a/U98tiX7gVS.json'

# ---- Introduction ----

def introduction():
    st_lottie(ecg_gfx, height=250)

    st.title("Introduction")
    introduction_text = """
    - Arrhythmia poses a significant challenge in cardiovascular medicine affecting around 2% of the population and causing thousands of deaths every year
    - It is marked by irregular heart rhythms with severe health implications like stroke and heart failure
    - Early arrhythmia detection is pivotal for timely treatment
    - Recent advancements in machine learning (ML) offer a promising future for automating arrhythmia detection through ECG analysis (Mincholé et al., 2019; Huda et al., 2020; Sakib, Fouda & Fadlullah, 2021)
    - Our main goal is to develop a machine learning model for accurate differentiation between cardiac arrhythmia presence and absence
    - Early detection is crucial for timely intervention and treatment (Zhang et al., 2017)
    - We also aim for scalability and generalizability, contributing to a framework that can be effectively implemented across various healthcare settings and populations
    """
    st.write(introduction_text)
    st.write("## Project Methodology")
        # Step 1
    st.subheader("Step 1: Preprocessing and Feature Engineering")
    st.write("""
    - Comprehensive preprocessing, including standardization, to ensure consistency and remove biases
    - Techniques like principal component analysis (PCA) to enhance ECG signal quality and capture relevant patterns
    """)
    # Step 2
    st.subheader("Step 2: Model Selection")
    st.write("""
    - Baseline models and more sophisticated models such as bagging and boosting
    - Techniques like GridsearchCV and Randomized Search for hyperparameter tuning 
    - Deep learning models such as Dense Neural Networks and Artificial Neural Networks
    """)
    # Step 3
    st.subheader("Step 3: Performance Evaluation")
    st.write("""
    - Thorough analysis of performance metrics like precision, recall, F1-score, and receiver operating characteristic (ROC) curves to assess model effectiveness
    - A main focus is placed on the number of undetected arrhythmia cases as evident in number of false negatives
    """)

# ---- Model Loading Function ----
# Define a function to load the models
@st.cache_resource
def load_uci_models():
    uci_models = {
        'Logistic Regression': joblib.load('uci_best_model_LogisticRegression.joblib'),
        'Random Forest': joblib.load('uci_best_model_RandomForestClassifier.joblib'),
        'Support Vector': joblib.load('uci_best_model_SVC.joblib'),
        'Elastic Net': joblib.load('uci_best_model_ElasticNet.joblib'),
        'Gradient Boosting': joblib.load('uci_best_model_GradientBoostingClassifier.joblib'),
        'AdaBoost': joblib.load('uci_best_model_AdaBoostClassifier.joblib'),
        'XGBoost': joblib.load('uci_best_model_XGBClassifier.joblib')
    }
    return uci_models

@st.cache_resource
def load_mit_models():
    mit_models = {
        'Logistic Regression': joblib.load('mit_best_model_LogisticRegression.joblib'),
        'Random Forest': joblib.load('mit_best_model_RandomForestClassifier.joblib'),
#        'Support Vector': joblib.load('mit_best_model_SVC.joblib'),
        'Elastic Net': joblib.load('mit_best_model_ElasticNet.joblib'),
        'Gradient Boosting': joblib.load('mit_best_model_GradientBoostingClassifier.joblib'),
        'AdaBoost': joblib.load('mit_best_model_AdaBoostClassifier.joblib'),
        'XGBoost': joblib.load('mit_best_model_XGBClassifier.joblib')
    }
    return mit_models

@st.cache_resource
def load_deep_learning_models():
    deep_learning_models ={    
        "DNN_relu": joblib.load('mit_best_model_DNN_relu.joblib'),
        "DNN_sigmoid": joblib.load('mit_best_model_DNN_sigmoid.joblib'),
        "DNN_tanh": joblib.load('mit_best_model_DNN_tanh.joblib'),
        "ANN_relu": joblib.load('mit_best_model_ANN_relu.joblib'),
        "ANN_sigmoid": joblib.load('mit_best_model_ANN_sigmoid.joblib'),
        "ANN_tanh": joblib.load('mit_best_model_ANN_tanh.joblib')
    }
    return deep_learning_models

# ---- UCI Bilkent Dataset ----

def uci_bilkent_dataset():
    st.title("UCI-Bilkent Dataset")
    selected_page = st.sidebar.selectbox("Select Page", ["Exploration", "Feature Engineering", "Modelling"])
    # Read UCI-Bilkent Dataset
    df = pd.read_csv('arrhythmia.csv')
    input_data = pd.read_csv('uci_x_test.csv')
    target_values = pd.read_csv('uci_y_test.csv')

    if selected_page == "Exploration":
        st.write("## Exploratory Data Analysis")
        st.dataframe(df.head(10))
        st.write(df.shape)
        st.dataframe(df.describe())

        if st.checkbox("Show NA"):
            st.dataframe(df.isna().sum())

        # Missing Values 
        df_obj = df.select_dtypes(include=['object']).columns
        for o in df_obj:
            df[o] = pd.to_numeric(df[o], errors='coerce')

        summary_df = df.isnull().sum()
        missing_stats = summary_df[summary_df != 0].reset_index()
        missing_stats.columns = ['column_name', 'no_of_missing']
        missing_stats['percent_missing'] = (missing_stats['no_of_missing'] / len(df)) * 100

        # Plotting the Missing Values
        st.write("## Missing Values")
        fig, ax = plt.subplots()
        ax.bar(missing_stats['column_name'], missing_stats['no_of_missing'])
        ax.set_title('Missing values')
        ax.set_xlabel('Column Names')
        ax.set_ylabel('Missing values')
        ax.set_xticklabels(missing_stats['column_name'], rotation=90)
        for i, value in enumerate(missing_stats['percent_missing']):
            ax.text(i, missing_stats['no_of_missing'][i], f"{value:.1f}%", ha='center', va='bottom')
        ax.set_ylim(0, len(df))
        st.pyplot(fig)

        # Distribution among Patient Age and Sex
        st.write("## Distribution of Patients Age and Sex")
        plt.figure(figsize=(10, 6))
        df.groupby('sex')['age'].plot(kind='hist', alpha=0.5, legend=True)
        plt.xlabel('Age')
        plt.ylabel('Frequency')
        plt.title('Distribution of Patients Age by Sex')
        plt.legend(['Female', 'Male'])

        # Pass the figure object to st.pyplot()
        st.pyplot(plt.gcf())

        # Distribution of Classes
        st.write("## Distribution of Classes")
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='class')
        plt.xlabel('Class')
        plt.ylabel('Count')
        plt.title('Distribution of Classes')
        st.pyplot(plt.gcf())

    elif selected_page == "Feature Engineering":
        st.header("Feature Engineering")
    
        # Load data
        df = pd.read_csv('UCI-BILKENT_Arrhythmia_Dataset_preprocessed_cleaned_classes_label.csv', sep=',', index_col=0)

        # Separate features and target variable
        X = df.drop(['class','label'], axis=1)  # Features
        y = df['label']  # Target variable

        # Standardize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Define a function to perform PCA and return transformed data
        def perform_pca(n_components):
            pca = PCA(n_components=n_components)
            X_pca = pca.fit_transform(X_scaled)
            return X_pca, pca.explained_variance_ratio_, pca.components_

        # Streamlit app
        st.subheader("PCA Visualization")
    
        # Slider for selecting number of PCA components
        st.write("Select the Number of PCA Components")
        n_components = st.select_slider("Number of PCA Components", options=[30, 40, 50, 60, 70, 78, 80, 90, 100])

        # Perform PCA
        X_pca, explained_variance_ratio, components = perform_pca(n_components)

        # Display cumulative variance ratio plot
        fig, ax = plt.subplots()
        ax.plot(range(1, n_components+1), explained_variance_ratio.cumsum(), marker='o', linestyle='-')
        ax.axhline(y=0.9, color='r', linestyle='--', label='90% Variance')
        ax.set_xlabel("Number of Components")
        ax.set_ylabel("Cumulative Variance Ratio")
        ax.set_title("Cumulative Variance Ratio vs. Number of Components")
        st.pyplot(fig)

        # Display explained variance ratio for each component
        st.subheader("Explained Variance Ratio for Each Component")
        fig2, ax2 = plt.subplots()
        ax2.plot(range(1, n_components+1), explained_variance_ratio, marker='o', linestyle='-')
        ax2.set_xlabel("Number of Components")
        ax2.set_ylabel("Explained Variance Ratio")
        ax2.set_title("Explained Variance Ratio for Each Component")
        st.pyplot(fig2)

        # Display principal components
        st.subheader("Principal Components")
        components_df = pd.DataFrame(components, columns=X.columns)
        st.write(components_df)

    elif selected_page == "Modelling":
#        st.write("## Systematic comparison of different Machine Learning Models for Arrhythmia Classification")
        st.write('### Hyperparameter space for GridSearchCV')
        data = {
            "Model": ["Logistic Regression", "Random Forest", "Support Vector", "Elastic Net", "Gradient Boosting", "AdaBoost", "XGBoost"],
            "Hyperparameter Space": [
                "solver: [liblinear, lbfgs]; C: np.logspace(-4, 2, 9)",
                "n_estimators: [10, 50, 100, 250, 500, 1000]; min_samples_leaf: [1, 3, 5]; max_features: [sqrt, log2]",
                "C: np.logspace(-4, 2, 9); kernel: [linear, rbf]",
                "C: np.logspace(-4, 2, 9); l1_ratio: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]",
                "n_estimators: [50, 100, 200]; learning_rate: [0.01, 0.1, 1.0]; max_depth: [3, 5, 7]",
                "n_estimators: [50, 100, 200]; learning_rate: [0.01, 0.1, 1.0]",
                "n_estimators: [50, 100, 200]; learning_rate: [0.01, 0.1, 1.0]; max_depth: [3, 5, 7]"]
        }
        hyperparameter_table = pd.DataFrame(data)
        st.table(hyperparameter_table)
        ####
        st.write("### Model Performance")
        models = ["Logistic Regression", "Random Forest", "SVC", "Elastic Net", "Gradient Boosting", "Ada Boosting", "XG Boosting"]
        best_parameters = ["C: 0.0032; solver: liblinear", 
                           "max_features: sqrt; min_samples_leaf: 3; n_estimators: 100",
                           "C: 0.01; kernel: linear", 
                           "C: 0.1; class_weight: balanced; fit_intercept: True; l1_ratio: 0.9; max_iter: 200; penalty: elasticnet; solver: saga; tol: 0.0001",
                           "learning_rate: 0.2; max_depth: 3; n_estimators: 100",
                           "base_estimator__max_depth: 2; base_estimator__min_samples_split: 2; learning_rate: 0.05; n_estimators: 150",
                           "learning_rate: 0.01; max_depth: 3; n_estimators: 200"]
        train_accuracy = [0.81, 0.98, 0.81, 0.82, 1.00, 0.73, 1.00]
        test_accuracy = [0.74, 0.73, 0.76, 0.73, 0.73, 0.64, 0.74]
        test_recall = [0.55, 0.60, 0.60, 0.60, 0.62, 0.53, 0.66]

        # Load multiple models
        models = load_uci_models()

        ## Model Results Comparisons ##
                
        st.write('### Model Performance Comparison')
        # Barplot with slider
        bar_width = 0.15
        index = np.arange(len(models))
        selected_model = st.select_slider("Select Model", options=list(models.keys()))  # Get the keys of the dictionary
        fig, ax = plt.subplots(figsize=(12, 8))
        model_index = list(models.keys()).index(selected_model)  # Find the index of the selected model key
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        #colors = ['lightblue', 'lightgreen', 'lightcoral', 'yellow']
        for i, model in enumerate(models):
            alpha = 1 if i == model_index else 0.4
            ax.bar(index[i] - 2*bar_width, test_accuracy[i], bar_width, color=colors[0], edgecolor='black', hatch='/', alpha=alpha)
            ax.bar(index[i] - bar_width, train_accuracy[i], bar_width, color=colors[1], edgecolor='black', hatch='\\', alpha=alpha)
            ax.bar(index[i], test_recall[i], bar_width, color=colors[2], edgecolor='black', hatch='x', alpha=alpha)
#            ax.bar(index[i] + bar_width, recall[i], bar_width, color=colors[3], edgecolor='black', hatch='.', alpha=alpha)
        ax.set_xlabel('Model')
        ax.set_ylabel('Scores')
        ax.set_title('Comparison of Model Performances')
        ax.set_xticks(index)    
        ax.set_xticklabels(list(models.keys()))  # Use the keys of the dictionary
        ax.legend(['Test Accuracy', 'Train Accuracy', 'Test Recall'], bbox_to_anchor=(1, 1), loc='upper left')
        st.pyplot(fig)

         # Define the test metrics
        test_metrics = {
            'Accuracy': 0.74,
            'Precision': 0.79,
            'Recall': 0.66,
            'F1-score': 0.72,
            'Auroc-score': 0.74
        }

        # Display the classification report
        st.header('Best Performing Model (XGBoost)')
        
        # Create a DataFrame for the classification report
        classification_report_df = pd.DataFrame(test_metrics, index=['XGBoost Model'])

        # Display the classification report DataFrame
        st.write('Classification Report:')
        st.write(classification_report_df)
        
# ---- MIT BIH Dataset ----

def mit_bih_dataset():
    # Read MIT-BIH Dataset
    df = pd.read_csv('MIT-BIH Arrhythmia Database.csv')
    input_data = pd.read_csv('mit_x_test.csv')
    target_values = pd.read_csv('mit_y_test.csv')

    st.title("MIT-BIH Dataset")
    selected_page = st.sidebar.selectbox("Select Page", ["Exploration and Preprocessing", "Modelling", "Deep Learning"])

    # Adjust MIT-BIH Arrhythmia Dataset and Preprocessing needed for both page 1 and 2 
    df_orig = df.copy() 
    class_names = {'N': 'Normal', 'SVEB': 'Supraventricular ectopic beat', 'VEB': 'Ventricular ectopic beat', 'F': 'Fusion beat', 'Q': 'Unknown beat'}
    df['type'] = df['type'].map(class_names)
    df_orig['type'] = df_orig['type'].map(class_names)
    # Create binary target variable
    class_mapping_lambda = lambda x: 0 if x == 'Normal' else 1
    df['label'] = df['type'].apply(class_mapping_lambda)
    df.drop(['type'], axis=1, inplace=True)
    X = df.drop('label', axis=1)
    y = df['label'] 
    majority_class = df[df['label'] == 0]
    minority_class = df[df['label'] == 1]
    downsampled_majority = resample(majority_class, replace=False, n_samples=len(minority_class), random_state=42)  
    balanced_df = pd.concat([downsampled_majority, minority_class])
    balanced_df = balanced_df.sample(frac=1, random_state=42)
    X_balanced = balanced_df.drop(['label'], axis=1)
    y_balanced = balanced_df['label']
    X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42)
#    input_data = X_test
#    target_values = y_test

    if selected_page == "Exploration and Preprocessing":
        st.write("## Exploratory Data Analysis and Preprocessing")
        st.write("### Data Exploration")
        exploration_text = """
        - The MIT-BIH Arrhythmia Database includes 48 half-hour segments of two-channel ambulatory ECG recordings from 47 subjects between 1975 and 1979 by the BIH Arrhythmia Laboratory (Moody & Mark, 2001)
        - Among these, 23 segments were randomly chosen from a pool of 4000 24-hour ambulatory ECG recordings at Boston's Beth Israel Hospital, while 25 segments were selected for less common yet clinically significant arrhythmias
        - Recordings were digitized at 360 samples per second per channel with an 11-bit resolution covering a 10 mV range
        - The dataset is freely available on PhysioNet (Goldberger et al., 2000)
        - The dataset already underwent advanced feature engineering (Sakib, Fouda & Fadlullah, 2021) and consists of 100,689 samples and 34 columns, with 33 features pertinent to ECG analysis and one target column for arrhythmia classifications
        - Features are split across two leads, Lead-II and Lead-V5, comprising 17 features each, contributing to the characterization of cardiac rhythms and morphologies: RR Intervals, Heartbeat Intervals, Heartbeat Amplitude Features, and Morphology Features
        """
        st.write(exploration_text)
        st.dataframe(df.head(10))
        st.write(df.shape)
        st.dataframe(df.describe())
        if st.checkbox("Show NA"):
            st.dataframe(df.isna().sum())
        # Plot distribution of types
        plt.figure(figsize=(10, 8))
        ax = sns.countplot(data=df_orig, x="type")
        plt.xticks(rotation=90, fontsize=16)
        plt.ylabel('Count', fontsize=16)
        plt.xlabel('Type', fontsize=16)
        plt.title('Distribution of Each Type', fontsize=20)
        for p in ax.patches:
            ax.annotate(format(p.get_height(), '.0f'), (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha='center', va='center', 
                   xytext=(0, 9), 
                   textcoords='offset points')
        plt.tight_layout()
        st.pyplot(plt)    
        st.write("### Creation of Binary Target Variable")
        # Plot pie chart   
        label_counts = df['label'].value_counts(normalize=True)
        plt.figure(figsize=(6, 6))
        plt.pie(label_counts, labels=['Normal', 'Arrhythmia'], explode=[0.05, 0.05], autopct="%0.2f%%")
        plt.title('Normal vs. Arrhythmia', fontsize=16)
        #st.pyplot(plt)
        ###
        st.write("### Downsampling to address Class Imbalance")
        downsampling_text = """
        - Before data augmentation, the dataset underwent several preprocessing steps
        - To handle class imbalance, a binary target variable was created for normal (label 0) and abnormal heartbeats (label 1), including unknown beats
        - Recordings were digitized at 360 samples per second per channel with an 11-bit resolution covering a 10 mV range
        - Feature scaling was performed using MinMaxScaler()
        - Given the large sample size of the MIT-BIH dataset, we downsampled data to the minority class of abnormal heartbeats
        """
        st.write(downsampling_text)
        st.write(f"Shape of the original dataset: {df.shape}")
        st.write(f"Shape of the downsampled dataset: {balanced_df.shape}")
        # Pie charts next to each other
        label_counts_original = np.bincount(df['label'].astype(int))
        label_counts_ds = np.bincount(balanced_df['label'].astype(int))
        fig, axes = plt.subplots(1, 2, figsize=(10, 8))
        axes[0].pie(label_counts_original, labels=['Normal', 'Arrhythmia'], explode=[0.05, 0.05], autopct="%0.2f%%")
        axes[0].set_title('Distribution before downsampling', fontsize=16)
        axes[1].pie(label_counts_ds, labels=['Normal', 'Arrhythmia'], explode=[0.05, 0.05], autopct="%0.2f%%")
        axes[1].set_title('Distribution after downsampling', fontsize=16)
        plt.tight_layout()
        st.pyplot(plt)

    elif selected_page == "Modelling":
#        st.write("## Systematic comparison of different Machine Learning Models for Arrhythmia Classification")
        st.write('### Hyperparameter space for Randomized Search ')
        hyperparameter_text = """
        - To optimize the hyperparamters, we utilized cross-validation and randomized search
        """
        st.write(hyperparameter_text)
        data = {
             "Model": ["Logistic Regression", "Random Forest", "Elastic Net", "Gradient Boosting", "AdaBoost", "XGBoost"],
            "Hyperparameter Space": [
        "solver: [liblinear, lbfgs]; C: np.logspace(-4, 2, 9)",
        "n_estimators: [10, 50, 100, 250, 500, 1000]; min_samples_leaf: [1, 3, 5]; max_features: [sqrt, log2]",
        "C: np.logspace(-4, 2, 9); l1_ratio: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]",
        "n_estimators: [50, 100, 200]; learning_rate: [0.01, 0.1, 1.0]; max_depth: [3, 5, 7]",
        "n_estimators: [50, 100, 200]; learning_rate: [0.01, 0.1, 1.0]",
        "n_estimators: [50, 100, 200]; learning_rate: [0.01, 0.1, 1.0]; max_depth: [3, 5, 7]"]
        }
        hyperparameter_table = pd.DataFrame(data)
        st.table(hyperparameter_table)
        #####
        st.write("### Model Performance")
        models = ["Logistic Regression", "Random Forest", "Elastic Net", "Gradient Boosting", "Ada Boosting", "XG Boosting"]
        best_parameters = ["C: 3.162; penalty: l2", "max_features: log2; min_samples_leaf: 1; n_estimators: 250",
                       "C: 0.01; l1_ratio: 0.4; max_iter: 1000; penalty: elasticnet; solver: saga",
                       "learning_rate: 0.1; max_depth: 7; n_estimators: 200",
                       "learning_rate: 1.0; n_estimators: 200",
                       "learning_rate: 1.0; max_depth: 7; n_estimators: 200"]
        train_accuracy = [0.88, 1.00, 0.86, 1.00, 0.96, 1.00]
        test_accuracy = [0.88, 0.97, 0.86, 0.98, 0.95, 0.98]
        precision = [0.90, 0.98, 0.91, 0.98, 0.95, 0.98]
        recall = [0.87, 0.98, 0.80, 0.98, 0.94, 0.98]
        f1_score = [0.88, 0.98, 0.85, 0.98, 0.95, 0.98]
        auroc_score = [0.88, 0.98, 0.86, 0.98, 0.95, 0.98]

        # Load multiple models
        models = load_mit_models()

        ## Model Results Comparisons ##
                
        #st.write('### Model Performance Comparison')
        # Plotting the bar chart without a slider
        bar_width = 0.2
        index = np.arange(len(models))
        fig, ax = plt.subplots(figsize=(14, 8))
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

        for i, model in enumerate(models):
            ax.bar(index[i] - bar_width, train_accuracy[i], bar_width, color=colors[0], edgecolor='black', hatch='/', alpha=1)
            ax.bar(index[i], test_accuracy[i], bar_width, color=colors[1], edgecolor='black', hatch='\\', alpha=1)
            ax.bar(index[i] + bar_width, recall[i], bar_width, color=colors[2], edgecolor='black', hatch='x', alpha=1)

        ax.set_xlabel('Model')
        ax.set_ylabel('Scores')
        ax.set_title('Comparison of Model Performances')
        ax.set_xticks(index)
        ax.set_xticklabels(list(models.keys()))
        ax.legend(['Train Accuracy', 'Test Accuracy', 'Recall'], bbox_to_anchor=(1, 1), loc='upper left')

        st.pyplot(fig)

        #st.write("### Comparison of Confusion Matrices")
        #image_path = "Figure_18.png"  
        #image = open(image_path, 'rb').read()
        #st.image(image, caption='Overall, Gradient Boost shows the smallest number of false negative. ', use_column_width=True)  

        ## Individual Model Results ##

        st.title('Model Results')
        results_text = """
        - By selecting the model below, the chosen model will run a live prediction on the test dataset and display the performance
        """
        st.write(results_text)
        train_data_size = len(df)
        test_data_size = len(input_data)
        st.write('Size of Test Dataset:', test_data_size)

        # Model selection widget
        selected_model = st.selectbox('Select Model', list(models.keys()))

        # Define a function to make predictions
        def predict(model, input_data):
            return model.predict(input_data)

        # Make prediction based on selected model
        if selected_model in models:
            prediction = predict(models[selected_model], input_data)

            # Display model attributes
            show_model_attributes = st.checkbox("Show Model Attributes")
            if show_model_attributes:
                st.subheader('Model Attributes:')
                model_attributes_box = st.empty()
                model_attributes = models[selected_model].get_params()
                model_attributes_box.write(model_attributes)

            # Display performance summary
            if hasattr(models[selected_model], 'score'):
                accuracy = models[selected_model].score(input_data, target_values)
                rounded_accuracy = round(accuracy, 4)
                st.subheader('Model Performance Summary:')
                st.write(f'Accuracy: {rounded_accuracy}')

            # Display classification report
            if hasattr(models[selected_model], 'predict'):
                st.subheader('Classification Report:')
                report = classification_report(target_values, prediction)
#                st.text(report)

                # Parse the classification report into a DataFrame
                report_data = []
                lines = report.split('\n')
                for line in lines[2:-5]:  # Skip the first two lines and last 5 lines
                    row = line.split()
                    if row:
                        class_name = row[0]
                        precision = float(row[1])
                        recall = float(row[2])
                        f1_score = float(row[3])
                        support = int(row[4])
                        report_data.append([class_name, precision, recall, f1_score])

                report_df = pd.DataFrame(report_data, columns=['Class', 'Precision', 'Recall', 'F1-Score'])

                # Display classification report as a table
#                st.write(report_df, index=False)

                # Convert DataFrame to HTML without index
                report_html = report_df.to_html(index=False)

                # Display classification report as a table without index
                st.markdown(report_html, unsafe_allow_html=True)

                # Create the Confusion Matrix
                st.subheader('Confusion Matrix:')
                cm = confusion_matrix(target_values, prediction)

                # Plot confusion matrix
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, square=True, ax=ax)
                ax.set_xlabel('Predicted') 
                ax.set_ylabel('Actual')

                # Display confusion matrix plot
                st.pyplot(fig)
        else:
            st.write('No model selected.')

    elif selected_page == "Deep Learning":
        st.write("## Comparison of different Neural Network Architectures for Arrhythmia Classification")
        st.write('### Dense Neural Networks')
        dnn_text = """
        - In our initial trial, we utilized a neural network architecture with four dense layers
        - The input layer handled inputs with a shape of (None, 32), corresponding to our dataset dimensions
        - The architecture included hidden layers with 10, 8, 6, and 3 neurons, totaling 493 trainable parameters
        - Training was conducted over 500 epochs using the adaptive Adam optimizer, ensuring stable and efficient weight updates
        - We evaluated three activation functions: Tanh, ReLU, and Sigmoid
        """
        st.write(dnn_text)
        st.write("#### Confusion Matrices for DNNs with different Activation Functions")
        image_path = "Figure_19.png"  
        image = open(image_path, 'rb').read()
        st.image(image, caption='', use_column_width=True)

        st.write('### Artificial Neural Networks')
        ann_text = """
        - We implemented an artificial neural network (ANN) with three hidden dense layers to capture intricate data patterns while mitigating overfitting
        - Each hidden layer had four neurons, tested with ReLU, Tanh, and Sigmoid activation functions
        - The output layer used a Sigmoid function for binary classification
        - Training involved 500 epochs with the adaptive Adam optimizer for stable weight updates
        """
        st.write(ann_text)
        nnx_text = """
        - For further refinement, we chose the best-performing neural network architecture, the DNN with ReLU activation, for additional trials
        - We also experimented with different learning rates (0.1, 0.01, 0.001) to find the optimal balance between convergence speed and stability
        - In our case, these experiments did not surpass the default Adam optimizer, which provided the best performance
        - The default Adam optimizer balanced convergence speed and stability, proving most effective for our dataset and model architecture"""
        st.write(nnx_text)        
        st.write("#### Confusion Matrices for ANNs with different Activation Functions")
        image_path = "Figure_20.png"  
        image = open(image_path, 'rb').read()
        st.image(image, caption='', use_column_width=True)
        st.write("ANN with three hidden dense layers four neurons each, with a sigmoid activation function in the output layer for binary classification, trained over 500 epochs with adaptive Adam optimizer")

        st.write("### Precision-Recall Curves for DNN and ANN Trials")
        image_path = "Figure_22.png"  
        image = open(image_path, 'rb').read()
        st.image(image, caption='', use_column_width=True)

# ---- Conclusions ----

def summary():
    st.header("Summary")
    summary_text = """
    - Optimizing for recall aligned with our objective of minimizing false negatives
    - Gradient Boosting achieved best recall with a high accuracy of 98%
    - DNN and ANN achieved accuracies ranging from 95% to 96%
    - Deep Learning models were outperformed by simpler ensemble models
    - One possible explanation for this discrepancy could be the dataset's size and complexity
    """

# Visualizations
    data = {
        'Model': ['Gradient Boosting', 'Random Forest', 'XG Boosting', 'DNN', 'Ada Boosting', 'Logistic Regression', 'ANN', 'Elastic Net'],
        'Test Accuracy': [0.98, 0.97, 0.98, 0.95, 0.95, 0.88, 0.94, 0.86],
        'Recall': [0.98, 0.98, 0.98, 0.95, 0.94, 0.87, 0.90, 0.80],
        'False negatives': [44, 47, 48, 49, 121, 347, 111, 419]
    }
    df = pd.DataFrame(data)
    df_sorted = df.sort_values(by='False negatives')
    # Add 1 to the index to start from 1
    df_sorted.index = range(1, len(df_sorted) + 1)
    # Add interactivity to the bar chart using Altair
    bars = alt.Chart(df_sorted).mark_bar().encode(
        y=alt.Y('Model:N', title='Model', sort='x'),  # Sorting by descending order of false negatives
        x=alt.X('False negatives:Q', title='Number of False Negatives'),
        color=alt.condition(
            alt.datum.Model == df_sorted.iloc[0]['Model'],
            alt.value('orange'),  # Color for the model with the fewest false negatives
            alt.value('steelblue')  # Default color for other models
        ),
        tooltip=['Test Accuracy:Q', 'Recall:Q']  # Show accuracy and recall on hover
    ).properties(
        title=''
    ).configure_axis(

    ).configure_title(
        fontSize=16,
        color='black'  
    ).configure_legend(
        titleColor='black',  
        labelColor='black'   
    )

    # Display the Altair chart
    st.write("### Model Ratings in terms of False Negatives:")
    st.altair_chart(bars, use_container_width=True)

    # Display conclusion text as bullet points with larger font size
    st.write(summary_text)

def explorations():
    st.header("Future Explorations")
    explorations_text = """
    - Exploration of additional advanced deep learning methodologies such as encoding-decoding techniques
    - Exploring different sampling strategies like including patient data from other hospitals or using GAN's 
    - Consultation with cardiologists for further collaborative exploration and optimization
    - Exploration of the classification of more nuanced heartbeat conditions
    - Exploring scalability detached from computational requirements, e.g. MiniML
    """
    st.write(explorations_text)
    
def references():
    st.header("References")
    references_text = """
    - Das, M. K., & Ari, S. (2014). ECG Beats Classification Using Mixture of Features. International Scholarly Research Notices, 2014, 178436. https://doi.org/10.1155/2014/178436
    - Goldberger, A., Amaral, L., Glass, L., Hausdorff, J., Ivanov, P. C., Mark, R., & Stanley, H. E. (2000). PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals. Circulation, 101(23), e215. https://doi.org/10.1161/01.cir.101.23.e215
    - Guvenir, H. A., Acar, B., Demiroz, G., & Cekin, A. (1997). A Supervised Machine Learning Algorithm for Arrhythmia Analysis. Proceedings of the Computers in Cardiology, 433-436.
    - Huda, N., Khan, S., Abid, R., Shuvo, S. B., Labib, M. M., & Hasan, T. (2020). A Low-cost, Low-energy Wearable ECG System with Cloud-Based Arrhythmia Detection. MedRxiv. https://doi.org/10.1101/2020.08.30.20184770
    - Moody, G. B., & Mark, R. G. (2001). The impact of the MIT-BIH Arrhythmia Database. IEEE Engineering in Medicine and Biology Magazine, 20(3), 45-50.
    - Mincholé, A., Camps, J., Lyon, A., & Rodríguez, B. (2019). Machine learning in the electrocardiogram. Journal of Electrocardiology, 57, 61–64. https://doi.org/10.1016/j.jelectrocard.2019.08.008
    - Lawless, S. T. (1994). Crying wolf: False alarms in a pediatric intensive care unit. Critical Care Medicine, 22, 981–985. PMID: 8205831
    - Lome, S. ECG Basics. Learn the Heart. Healio. https://www.healio.com/cardiology/learn-the-heart/ecg-review/ecg-interpretation-tutorial/qrs-complex
    - Ramirez-Santana, M. (2018). Limitations and Biases in Cohort Studies. InTech. https://doi.org/10.5772/intechopen.74324
    - Sakib, S., Fouda, M. M., & Fadlullah, Z. M. (2021). Harnessing Artificial Intelligence for Secure ECG Analytics at the Edge for Cardiac Arrhythmia Classification. Secure Edge Computing, 1, 137-153. CRC Press. ISBN: 9781003028635
    - Tachycardia (Fast Heart Rate) in Children. Ann & Robert H. Lurie Children’s Hospital of Chicago. https://www.luriechildrens.org/en/specialties-conditions/tachycardia/
    - Tan, K. F., Chan, K. L., & Choi, K. (2000). Detection of the QRS complex, P wave and T wave in electrocardiogram. 2000 First International Conference Advances in Medical Signal and Information Processing (IEE Conf. Publ. No. 476), 41-47.
    - Wang, D., Zhang, L., Wang, Z.-Y., Zhang, Z.-Y., & Wang, Y. (2017). The missed diagnosis of aortic dissection in patients with acute myocardial infarction: A disastrous event. Journal of Thoracic Disease, 9(7), E636-E639. https://doi.org/10.21037/jtd.2017.06.103
    """
    st.write(references_text)
    
def conclusions():
    st.title("Conclusions")
    selected_page = st.sidebar.selectbox("Select Page", ["Summary", "Future Explorations", "References"])
    if selected_page == "Summary":
        summary()
    elif selected_page == "Future Explorations":
        explorations()
    elif selected_page == "References":
        references()
        

# ---- Main / Sidebar ----

def main():
    st.sidebar.title("Arrhythmia Classification Experiments on the MIT-BIH Dataset")
    page = st.sidebar.radio("Comparisons of various machine learning and deep learning algorithms, Spring 2024", ["Introduction", "AI Model Performance", "Conclusions"])
    if page == "Introduction":
        introduction()
#    elif page == "UCI-Bilkent Dataset":
#        uci_bilkent_dataset()
    elif page == "AI Model Performance":
        mit_bih_dataset()
    elif page == "Conclusions":
        conclusions()

if __name__ == "__main__":
    main()
