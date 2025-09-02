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
        self.fraud_vs_non_fraud()
    




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

    
    def prep_counts(self,df, by):
        agg = df.groupby([by], dropna=False)["fraud_flag"].agg(
            fraud="sum", total="count"
        ).reset_index()
        agg["non_fraud"] = agg["total"] - agg["fraud"]
        return agg
    
    def fraud_vs_non_fraud(self):
        temp_df=self.df.copy()
        st.subheader("Fraud vs Non-Fraud — Grouped Bars")

        tab1,tab2= st.tabs(["Chart","Description"])
        
        with tab1:
            tab_txn, tab_device, tab_network = st.tabs(["Transaction Type", "Device Type", "Network Type"])  # [web:214]

            with tab_txn:
                col = "type"
                agg = self.prep_counts(temp_df, col)
                long_df = agg.melt(id_vars=[col], value_vars=["fraud","non_fraud"],
                                var_name="class", value_name="count")
                fig = px.bar(long_df, x=col, y="count", color="class", barmode="group",
                            title="By Transaction Type", template="plotly_white")
                fig.update_layout(legend_title_text="", xaxis_title="", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)  # [web:202]

            with tab_device:
                col = "device_type"
                agg = self.prep_counts(temp_df, col)
                long_df = agg.melt(id_vars=[col], value_vars=["fraud","non_fraud"],
                                var_name="class", value_name="count")
                fig = px.bar(long_df, x=col, y="count", color="class", barmode="group",
                            title="By Device Type", template="plotly_white")
                fig.update_layout(legend_title_text="", xaxis_title="", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)  # [web:202]

            with tab_network:
                col = "network_type"
                agg = self.prep_counts(temp_df, col)
                long_df = agg.melt(id_vars=[col], value_vars=["fraud","non_fraud"],
                                var_name="class", value_name="count")
                fig = px.bar(long_df, x=col, y="count", color="class", barmode="group",
                            title="By Network Type", template="plotly_white")
                fig.update_layout(legend_title_text="", xaxis_title="", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)  # [web:202]
        
        with tab2:
            st.markdown("""
            ### Fraud concentration overview
            - :blue[Transaction types:] **P2M** and **P2P** show the highest fraud counts, indicating attacker focus on merchant payments and peer transfers where urgency and social prompts are common.
            - :blue[Device type:] **Android ~350** frauds vs **Web ~26** and **iOS ~30**, reflecting a mobile-first exposure and broader attack surface on Android.
            - :blue[Network type:] Higher counts align with higher-throughput networks — **4G ~149k**, **5G ~62k**, **Wi‑Fi ~25k**, **3G ~12k** — suggesting more traffic enables more attempts.

            ### Interpretation
            - :blue[Why P2M/P2P?] **P2M** often correlates with promo-driven purchases and fake merchant impersonation, while **P2P** is prone to social-engineering “urgent transfer” schemes.
            - :blue[Why Android?] Larger user base and APK ecosystem risk increase exposure; **Web/iOS** lower counts likely reflect smaller share and platform controls.
            - :blue[Why 4G/5G?] Faster networks facilitate rapid attempts and bursts; **Wi‑Fi** peaks can reflect public hotspot risks; **3G** is lower in line with usage.

            ### Recommended actions
            - :blue[Type-focused controls:] Tighten velocity limits, beneficiary risk scoring, and step-up authentication for **P2M** and **P2P**, especially during promotions and weekends.
            - :blue[Device-aware hardening:] Strengthen device fingerprinting and runtime integrity on **Android**; surface contextual in‑app scam warnings pre‑transaction.
            - :blue[Network-aware policies:] Apply stricter thresholds on **4G/5G** high-velocity patterns; mark risky **Wi‑Fi** contexts for additional verification.

            ### Talk track
            - :blue[Where is fraud concentrated?] **P2M/P2P**, **Android**, and high-throughput networks (**4G/5G**).
            - :blue[So what?] Prioritize dynamic limits, step‑up checks, and behavioral profiling on these contexts to reduce loss with minimal friction.
            - :blue[Expected impact] Faster suppression of high-volume attack paths while minimizing false positives through targeted controls.
            """)

                    
                    