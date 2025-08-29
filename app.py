import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dataloader import Dataloader

#classes
from classes.transaction_patterns import Transaction

st.title("Unified Payments (UPI) Fraud Analytics")


st.set_page_config(layout='wide',page_title="UPI Analytics")


#loading dataset
dataloader= Dataloader("dataset\cleaned_v1.csv")
df=dataloader.df

st.sidebar.title("UPI Analytics")

option=st.sidebar.selectbox("Select One",["Transaction Patterns","Demographic Insights","Temporal Patterns","Fraud Insights"])

if option== "Transaction Patterns":
    transaction = Transaction(df)
