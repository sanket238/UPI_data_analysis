import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

class Transaction:
    def __init__(self, data):
        # data is expected to be a pandas DataFrame with an 'amount' column
        self.df = data
        self.visualize()

    def visualize(self):
        st.subheader("Transaction Patterns: Amount Summary",divider=True)

        # Basic validation
        if not isinstance(self.df, pd.DataFrame) or 'amount' not in self.df.columns:
            st.error("Input must be a DataFrame that includes an 'amount' column.")
            return

        # Describe statistics for 'amount'
        desc = self.df['amount'].describe().to_frame(name='amount')

        # Optional: Format numeric precision for readability
        desc_fmt = desc.copy()
        desc_fmt['amount'] = desc_fmt['amount'].map(lambda x: f"{x:,.6f}")

        st.subheader("Description of Amount Coulmn")

        # Explanatory bullets
        # Metrics row
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(desc_fmt, use_container_width=False)
        with col2:
            # Explanatory bullets
            st.subheader("Distribution Insight")
            st.markdown(
                """
            - Since the :blue-background[**mean**] is much higher than the :blue-background[**median**], the distribution is **right-skewed**.  
            - Most transactions are relatively small, but a few very large transactions (like the 33,061 maximum) pull the mean up.
            - :blue-background[**Std**] = 1833.59, which is larger than the mean → high variability.
            - :blue-background[**25% percentile**] = 287, :blue-background[**75% percentile**] = 1588 → the interquartile range (IQR) is 1301.
            - This shows that 50% of all transactions fall between ₹287 and ₹1588 (mostly low to mid-value).
                """
            )
        # Histogram of amounts
        st.subheader("Amount distribution",divider=True)
        fig, ax = plt.subplots(figsize=(10, 4))  # adjust size as needed
        sns.histplot(self.df['amount'], bins=50, kde=True, ax=ax)
        ax.set_xlabel("Amount")
        ax.set_ylabel("Count")
        ax.set_title("Histogram of Transaction Amounts (with KDE)")
        st.pyplot(fig)

        #customer transcation behavior
        st.subheader("Customer Transaction Behavior", divider=True)
        st.markdown(
            """
        - We wanted to understand customer transaction behavior — what’s a typical transaction and where the outliers are?  
        - As we can see, most transactions are very small, but a few very large ones stretch the scale, making it hard to see the main trend.  
        - When we scale the data to reduce the effect of outliers, we find that most customers typically transact between :blue-background[**₹300**] and :blue-background[**₹3,000**], with the most common value being around :blue-background[**₹300–₹400**].  
        - A small number of high-value transactions (about :blue-background[**₹30,000**]) exist, but they’re rare.  
        - While the average transaction is :blue-background[**₹1,300**], that number is misleading — it’s pulled up by a few very large transfers. When we adjust for scale, we see that the typical customer spends :blue-background[**₹300–₹400**] per transaction. The majority of activity is in the :blue-background[**₹100–₹3,000**] range, and very large transactions (around :blue-background[**₹30,000**]) are rare but important for fraud monitoring.  
            """
        )

        self.boxplot()
        
    def boxplot(self):
        st.subheader("Boxplots: Raw vs Transformed", divider=True)

        # Ensure the transformed column exists; create if needed (example: log1p)
        if 'amount_transform' not in self.df.columns:
            self.df['amount_transform'] = np.log10(self.df['amount'])  # optional example transform

        col1, col2 = st.columns(2)

        with col1:
            st.caption("Before transformation")
            fig1, ax1 = plt.subplots(figsize=(5, 3.5))
            sns.boxplot(x=self.df['amount'], ax=ax1)
            ax1.set_xlabel("Amount")
            ax1.set_title("Raw Amounts")
            fig1.tight_layout()
            st.pyplot(fig1)

        with col2:
            st.caption("After transformation")
            fig2, ax2 = plt.subplots(figsize=(5, 3.5))
            sns.boxplot(x=self.df['amount_transform'], ax=ax2)
            ax2.set_xlabel("Transformed Amount")
            ax2.set_title("Log-Transformed Amounts")
            fig2.tight_layout()
            st.pyplot(fig2)

        # Explanatory markdown
        st.markdown(
            """
        On the raw scale, the boxplot shows a long tail with extreme outliers up to :blue-background[**₹33,000**], while most data is compressed below :blue-background[**₹3,000**].  
        To better understand the central trend, a log-transformed boxplot reveals that the majority of transactions lie between :blue-background[**₹300–₹3,000**].
            """
        )
    

            

        


