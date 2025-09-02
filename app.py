import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dataloader import Dataloader

#classes
from classes.transaction_patterns import Transaction
from classes.demographic import Demographic
from classes.temporal import Temporal
from classes.fraud_insights import FraudInsights

st.title("Unified Payments (UPI) Fraud Analytics")


st.set_page_config(layout='wide',page_title="UPI Analytics")


#loading dataset
dataloader= Dataloader("dataset\cleaned_v1.csv")
df=dataloader.df
df.rename(columns={"sender_age_group":"age_group"},inplace=True)
df.drop(columns="receiver_age_group",inplace=True)



st.sidebar.title("UPI Analytics")

option=st.sidebar.selectbox("Select One",["Transaction Patterns","Demographic Insights","Temporal Patterns","Fraud Insights"])

if option== "Transaction Patterns":
    transaction = Transaction(df)
elif option== "Demographic Insights":
    demographic= Demographic(df)
elif option== "Temporal Patterns":
    temporal= Temporal(df)
elif option=="Fraud Insights":
    fraud= FraudInsights(df)

