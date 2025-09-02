import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly_express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class FraudInsights():
    
    def __init__(self,data):
        self.df=data
        self.visualize()
    
    def visualize(self):
        self.fraud_rate()
    
    # Helper: compute rate table for a given categorical column
    def fraud_rate_by(self,df, col):
        g = df.groupby(col, dropna=False)["fraud_flag"].agg(
            fraud_count="sum",
            total_count="count",
        ).reset_index()
        g["fraud_rate_pct"] = np.where(g["total_count"] > 0,(g["fraud_count"] / g["total_count"])*100, 0.0)
        return g.sort_values("fraud_rate_pct", ascending=False)

    def fraud_rate(self):
        temp_df=self.df.copy(deep=True)
        temp_df["fraud_flag"] = pd.to_numeric(temp_df["fraud_flag"], downcast="integer")



        # Overall fraud rate
        overall = self.df["fraud_flag"].agg(fraud_count="sum", total_count="count")
        overall_rate = float(overall["fraud_count"]) / float(overall["total_count"]) * 100.0 if overall["total_count"] else 0.0
       


        st.markdown("## Fraud rate overview")
        st.markdown(f"- :blue[Overall fraud rate:] **{overall_rate:.2f}%**")
        st.caption(
            "Values range 0–1 (e.g., 0.0015 = 0.15%); higher values indicate a larger share of transactions are fraudulent."
        )

        # Compute by category
        by_txn = self.fraud_rate_by(temp_df, "type")            # transaction_type column is assumed as 'type'
        by_device = self.fraud_rate_by(temp_df, "device_type")
        by_network = self.fraud_rate_by(temp_df, "network_type")

        # Bar charts
        tab1, tab2, tab3 = st.tabs(["Transaction", "Device","Network"])
        with tab1:
            st.subheader("By Transaction type")
            fig_txn = px.bar(
                by_txn, x="fraud_rate_pct", y="type", orientation="h",
                text=by_txn["fraud_rate_pct"].map(lambda v: f"{v:.2f}%"),
                labels={"fraud_rate_pct": "Fraud Rate (%)", "type": "Transaction Type"},
                template="plotly_white",
            )
            fig_txn.update_traces(marker_color="crimson", textposition="outside")
            fig_txn.update_layout(xaxis_tickformat=".2f")
            st.plotly_chart(fig_txn)

        with tab2:

            st.subheader("By Device type")
            fig_dev = px.bar(
                by_device, x="fraud_rate_pct", y="device_type", orientation="h",
                text=by_device["fraud_rate_pct"].map(lambda v: f"{v:.2f}%"),
                labels={"fraud_rate_pct": "Fraud Rate (%)", "device_type": "Device Type"},
                template="plotly_white",
            )
            fig_dev.update_traces(marker_color="steelblue", textposition="outside")
            fig_dev.update_layout(xaxis_tickformat=".2f")
            st.plotly_chart(fig_dev)
        with tab3:

            st.subheader("By Network type")
            fig_net = px.bar(
                by_network, x="fraud_rate_pct", y="network_type", orientation="h",
                text=by_network["fraud_rate_pct"].map(lambda v: f"{v:.2f}%"),
                labels={"fraud_rate_pct": "Fraud Rate (%)", "network_type": "Network Type"},
                template="plotly_white",
            )
            fig_net.update_traces(marker_color="darkorange", textposition="outside")
            fig_net.update_layout(xaxis_tickformat=".2f")
            st.plotly_chart(fig_net)

        
        