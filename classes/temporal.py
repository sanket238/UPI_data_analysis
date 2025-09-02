import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly_express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Temporal:
    
    def __init__(self,data):
        self.df=data
        self.visualize()
    
    def visualize(self):
        st.subheader("Transactions by Hour, Day, and Weekend")
        tab1, tab2 = st.tabs(["Chart", "Description"])
        with tab1:
            hour_labels = {h: pd.to_datetime(str(h), format="%H").strftime("%I %p") for h in range(24)}
            hourly = (
                self.df.groupby(["hour_of_day", "is_weekend"])
                .size()
                .reset_index(name="transaction_count")
            )
            hourly["Day Type"] = hourly["is_weekend"].map({
                1: "Weekend",
                0: "Weekday"
            })
            hourly["hour_label"] = hourly["hour_of_day"].map(hour_labels)

            fig = px.histogram(
            hourly,
            x="hour_label",
            y="transaction_count",
            color="Day Type",
            barmode="group",   # side-by-side comparison
            nbins=24,          # 24 bins for 24 hours
            )

            fig.update_layout(
            xaxis=dict(title="Hour of Day", dtick=1),
            yaxis=dict(title="Number of Transactions"),
            bargap=0.2,
            legend_title="Day Type"
            )

            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:

            st.markdown("## Normal Transaction Behavior")
            st.markdown("- Transactions remain :blue[very low between 12 AM – 6 AM] and rise sharply after 7 AM.")
            st.markdown("- Peak activity occurs during :blue[11 AM – 8 PM], especially in evening hours (5–7 PM).")
            st.markdown("- Weekday transactions are consistently :blue[higher] than weekends, following a stable hourly pattern.")

            st.markdown("---")

            st.markdown("## Fraud Monitoring Relevance")
            st.markdown("- :blue[Off-hour transactions (late night / early morning)] are naturally low — any unusual spike here could indicate :blue[potential fraudulent behavior].")
            st.markdown("- :blue[Sudden deviations] from the weekday–weekend pattern may signal :blue[abnormal activity].")
            st.markdown("- Fraud systems should :blue[tighten anomaly detection thresholds during low-volume hours] (midnight to 6 AM), where genuine activity is minimal.")
            st.markdown("- During peak hours, fraud detection must rely on :blue[behavioral profiling] (e.g., unusual amounts, locations, or rapid-fire transactions).")

        
        st.subheader("Time-Series for Fraud vs Non Fraud Transactions")
        time_tab1, time_tab2= st.tabs(["Charts","Description"])
        with time_tab1:
            self.time_series()
        with time_tab2:
            st.markdown("""
            ### Festival-season impact
            - :blue[Higher transaction volume] is observed in festival-adjacent months, aligning with typical October–November spikes from festive shopping and promos.
            - :blue[Fraud counts] co-move upward in the same window, indicating intensified attempts during high-traffic periods.

            ### Fraud ratio pattern
            - The :blue[fraud rate (percentage of transactions that are fraud)] trends higher in festival months, suggesting not just more fraud by count but a **larger share** of activity turning fraudulent.
            - :blue[Interpretation:] urgency, promotions, and more inexperienced spenders increase susceptibility; tighten controls during these weeks.

            ### What this means operationally
            - :blue[Seasonal hardening:] apply stricter anomaly thresholds and velocity checks in Sep–Nov (and late Dec) while maintaining user experience for trusted profiles.
            - :blue[Context features:] add an **is_festival_window** flag and promotion intensity features to models; monitor drift and recalibrate post-season.
            - :blue[User nudges:] in-app warnings on phishing/refund scams during peaks can reduce social-engineering losses.
            """)

    

    def time_series(self):
        #making copy of original dataset
        temp_df=self.df.copy(deep=True)
        temp_df["_dt"] = pd.to_datetime(temp_df['date'],errors="coerce")
        temp_df["fraud_flag"] = temp_df["fraud_flag"].astype("int8")
        temp_df["non_fraud"] = 1 - temp_df["fraud_flag"]
        # ---------- Daily base ----------
        daily = (
            temp_df
                .set_index("_dt")  # or skip if already index; or use .resample("D", on="date")
                .resample("D")
                .agg({"fraud_flag": "sum", "non_fraud": "sum"})  # single pass aggregation [7][11]
                .rename(columns={"fraud_flag": "fraud"})
        )

        daily_smoothed = daily.rolling(window=7, min_periods=1).mean()
        # ---------- Monthly aggregations ----------
        monthly_raw = daily.resample("M").sum()
        monthly_smooth = daily_smoothed.resample("M").sum()
        for m in (monthly_raw, monthly_smooth):
            m["total"] = m["fraud"] + m["non_fraud"]
            m["fraud_rate"] = np.where(m["total"] > 0, m["fraud"] / m["total"], 0.0)
        


        fig1 = make_subplots(specs=[[{"secondary_y": True}]])  # Enable secondary axis. [web:52][web:70]

        # Raw traces (visible)
        fig1.add_trace(
            go.Scatter(x=monthly_raw.index, y=monthly_raw["fraud"],
                    name="Fraud (Raw)", mode="lines+markers",
                    line=dict(color="crimson")),
            secondary_y=False
        )
        fig1.add_trace(
            go.Scatter(x=monthly_raw.index, y=monthly_raw["non_fraud"],
                    name="Non-Fraud (Raw)", mode="lines+markers",
                    line=dict(color="steelblue")),
            secondary_y=True
        )

        # Smoothed traces (legend-only)
        fig1.add_trace(
            go.Scatter(x=monthly_smooth.index, y=monthly_smooth["fraud"],
                    name="Fraud (Smoothed 7d→M)", mode="lines+markers",
                    line=dict(color="firebrick", dash="dash"), visible="legendonly"),
            secondary_y=False
        )
        fig1.add_trace(
            go.Scatter(x=monthly_smooth.index, y=monthly_smooth["non_fraud"],
                    name="Non-Fraud (Smoothed 7d→M)", mode="lines+markers",
                    line=dict(color="dodgerblue", dash="dash"), visible="legendonly"),
            secondary_y=True
        )

        fig1.update_layout(
            title="Counts per Month — Dual Axis",
            xaxis_title="Month",
            yaxis_title="Fraud Count",
            legend_title_text="Series",
            template="plotly_white",
            hovermode="x unified"
        )
        fig1.update_yaxes(title_text="Non-Fraud Count", secondary_y=True)

        st.plotly_chart(fig1, use_container_width=True)  # Multiple axes with secondary_y

        # ---------- Chart 2: Bars (total) + line (fraud rate %) with secondary y ---------

        fig2 = make_subplots(specs=[[{"secondary_y": True}]])  # Secondary y for rate

        # Bars: total volume (raw visible; smoothed legend-only)
        fig2.add_trace(
            go.Bar(x=monthly_raw.index, y=monthly_raw["total"],
                name="Total Volume (Raw)", marker_color="lightgray"),
            secondary_y=False
        )
        fig2.add_trace(
            go.Bar(x=monthly_smooth.index, y=monthly_smooth["total"],
                name="Total Volume (Smoothed 7d→M)", marker_color="gainsboro",
                visible="legendonly"),
            secondary_y=False
        )

        # Line: fraud rate % (raw visible; smoothed legend-only)
        fig2.add_trace(
            go.Scatter(x=monthly_raw.index, y=monthly_raw["fraud_rate"] * 100.0,
                    name="Fraud Rate % (Raw)", mode="lines+markers",
                    line=dict(color="darkorange")),
            secondary_y=True
        )
        fig2.add_trace(
            go.Scatter(x=monthly_smooth.index, y=monthly_smooth["fraud_rate"] * 100.0,
                    name="Fraud Rate % (Smoothed 7d→M)", mode="lines+markers",
                    line=dict(color="orange", dash="dash"), visible="legendonly"),
            secondary_y=True
        )

        # Layout
        fig2.update_layout(
            title="Monthly Volume + Fraud Rate",
            xaxis_title="Month",
            yaxis_title="Total Transactions",
            legend_title_text="Series",
            template="plotly_white",
            barmode="overlay",
            hovermode="x unified"
        )
        fig2.update_yaxes(
            title_text="Fraud Rate (%)",
            secondary_y=True,
            rangemode="tozero"
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.caption(
            "Monthly series built from daily resampling; optional smoothing applied on daily then summed monthly. "
            "Legend toggles  compare Raw vs Smoothed without sidebar controls."
        )