# -*- coding: utf-8 -*-
"""app1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19hFZsMfe5exd5O6rJ3rrx_tYJatOvi2q
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

st.set_page_config(page_title="Titanic Survivor Prediction", layout="wide")
st.title("Titanic Survivor Prediction ML Project")

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = None
if 'scaler' not in st.session_state:
    st.session_state.scaler = None

file_idt = "1Pf-t_SyT20sJ3lhxhzhJJ1G7dVKw5zdV"
urlt = f"https://drive.google.com/uc?id={file_idt}"
df = pd.read_csv(urlt)
df.head()

if urlt:
    df = pd.read_csv(urlt)

    st.subheader("Raw Data")
    st.dataframe(df.head())

    # Prediction UI
    st.subheader("Fill & submit the data to check - Passenger Survival Prediction")

    with st.form("prediction_form"):
        pclass = st.selectbox("Ticket Class (Pclass)", [1, 2, 3])
        sex = st.selectbox("Sex", ["male", "female"])
        age = st.slider("Age", 0, 80, 30)
        sibsp = st.number_input("Siblings/Spouses Aboard (SibSp)", min_value=0, max_value=10, value=0)
        parch = st.number_input("Parents/Children Aboard (Parch)", min_value=0, max_value=10, value=0)
        fare = st.number_input("Fare Paid", min_value=0.0, max_value=600.0, value=32.2)
        embarked = st.selectbox("Port of Embarkation", ["S", "C", "Q"])

        submit = st.form_submit_button("Predict")

    if submit:
        sex_enc = 1 if sex == "female" else 0
        embarked_enc = {"S": 2, "C": 0, "Q": 1}[embarked]

        input_data = pd.DataFrame([{
            "Pclass": pclass,
            "Sex": sex_enc,
            "Age": age,
            "SibSp": sibsp,
            "Parch": parch,
            "Fare": fare,
            "Embarked": embarked_enc
        }])

        input_scaled = st.session_state.scaler.transform(input_data)
        prediction = st.session_state.model.predict(input_scaled)[0]
        prob = st.session_state.model.predict_proba(input_scaled)[0][prediction]

        if prediction == 1:
            st.success(f"Good News - The passenger would have SURVIVED! (Confidence: {prob:.2%})")
        else:
            st.error(f"Bad news - The passenger would NOT have survived. (Confidence: {prob:.2%})")

    # EDA
    st.subheader("Data Analysis - Explaination")
    with st.expander("Basic Information"):
        st.write(df.describe())
        st.write(df.info())
        st.write(df.isnull().sum())

    with st.expander("Visualizations"):
        fig1, ax1 = plt.subplots()
        sns.countplot(x='Survived', data=df, ax=ax1)
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots()
        sns.countplot(x='Sex', hue='Survived', data=df, ax=ax2)
        st.pyplot(fig2)

        fig3, ax3 = plt.subplots()
        sns.countplot(x='Pclass', hue='Survived', data=df, ax=ax3)
        st.pyplot(fig3)

        fig4, ax4 = plt.subplots()
        sns.boxplot(x='Pclass', y='Age', data=df, ax=ax4)
        st.pyplot(fig4)

    # Preprocessing
    st.subheader("Preprocessing & Model Training (Automatic)")
    df['Age'].fillna(df['Age'].median(), inplace=True)
    df['Embarked'].fillna(df['Embarked'].mode()[0], inplace=True)
    df.drop(['Cabin', 'PassengerId', 'Name', 'Ticket'], axis=1, inplace=True)

    le = LabelEncoder()
    df['Sex'] = le.fit_transform(df['Sex'])
    df['Embarked'] = le.fit_transform(df['Embarked'])

    X = df.drop('Survived', axis=1)
    y = df['Survived']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    st.session_state.model = model
    st.session_state.scaler = scaler

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    cm = confusion_matrix(y_test, preds)
    report = classification_report(y_test, preds, output_dict=True)

    st.success(f"Model trained! Accuracy: {acc:.4f}")
    st.write("### Confusion Matrix")
    st.dataframe(cm)
    st.write("### 📄 Classification Report")
    st.dataframe(pd.DataFrame(report).transpose())

    st.write("### Feature Importances")
    importances = model.feature_importances_
    feature_names = df.drop('Survived', axis=1).columns
    fi_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances}).sort_values(by="Importance", ascending=False)

    fig_imp, ax_imp = plt.subplots()
    sns.barplot(x='Importance', y='Feature', data=fi_df, ax=ax_imp)
    st.pyplot(fig_imp)