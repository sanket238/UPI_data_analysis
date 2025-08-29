import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dataloader import Dataloader

st.title("Unified Payments (UPI) Fraud Analytics")


st.set_page_config(layout='wide',page_title="UPI Analytics")


#loading dataset
dataloader= Dataloader("dataset\cleaned_v1.csv")
df=dataloader.df

st.sidebar.title("UPI Analytics")

option=st.sidebar.selectbox("Select One",["Transaction Patterns","Demographic Insights","Temporal Patterns","Fraud Insights"])