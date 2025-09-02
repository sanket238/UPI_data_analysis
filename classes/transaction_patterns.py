import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

class Transaction:
    def __init__(self, data):
        self.df = data
        self.df['amount_transform'] = np.log10(self.df['amount']) 
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
            st.dataframe(desc_fmt, use_container_width=True)
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
        
        st.subheader("Amount distribution",divider=True)
        #tabs for histogram and description
        hist1, hist2,hist3= st.tabs(["Chart","Description","Boxplots"])
        with hist1:
            self.histogram()
        with hist2:
            self.histogram_description()
        with hist3:
            self.boxplot()
        
        col3, col4= st.columns(2)
        
        with col3:
            self.frequency_type()
            

        with col4:
            self.top_merchants()
   



    def histogram(self):
        # Histogram of amounts
        hist_tab_before, hist_tab_after = st.columns(2)
        
        with hist_tab_before:
            st.caption("Before Transformation")
            fig, ax = plt.subplots(figsize=(8, 4))  
            sns.histplot(self.df['amount'], bins=50, kde=True, ax=ax)
            ax.set_xlabel("Amount")
            ax.set_ylabel("Count")
            ax.set_title("Histogram of Transaction Amounts (with KDE)")
            st.pyplot(fig)
        
        with hist_tab_after:
            st.caption("After Transformation")
            fig, ax= plt.subplots(figsize=(8,4))
            sns.histplot(self.df['amount_transform'],bins=50,kde=True,ax=ax)
            ax.set_xlabel("Amount")
            ax.set_ylabel("Count")
            ax.set_title("Histogram of Transaction After Transformation")
            st.pyplot(fig)
        
    
    def histogram_description(self):

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

    def boxplot(self):
        st.markdown("### Boxplots Raw vs Transformed")
        # Ensure the transformed column exists; create if needed (example: log1p)
        if 'amount_transform' not in self.df.columns:
            self.df['amount_transform'] = np.log10(self.df['amount'])  # optional example transform

        box1, box2,box3 = st.columns(3)

        with box1:
            st.caption("Before transformation")
            fig1, ax1 = plt.subplots(figsize=(5, 3.5))
            sns.boxplot(x=self.df['amount'], ax=ax1)
            ax1.set_xlabel("Amount")
            ax1.set_title("Raw Amounts")
            fig1.tight_layout()
            st.pyplot(fig1)
        with box2:
            st.caption("After transformation")
            fig2, ax2 = plt.subplots(figsize=(5, 3.5))
            sns.boxplot(x=self.df['amount_transform'], ax=ax2)
            ax2.set_xlabel("Transformed Amount")
            ax2.set_title("Log-Transformed Amounts")
            fig2.tight_layout()
            st.pyplot(fig2)
        with box3:
            self.box_description()


    def box_description(self):
        # Explanatory markdown
        st.caption("Description")
        st.markdown(
            """
        On the raw scale, the boxplot shows a long tail with extreme outliers up to :blue-background[**₹33,000**], while most data is compressed below :blue-background[**₹3,000**].  
        To better understand the central trend, a log-transformed boxplot reveals that the majority of transactions lie between :blue-background[**₹300–₹3,000**].
            """
        )
    
    def frequency_type(self):
        st.subheader("Frequency of different transcation type",divider=True)
        freq1_chart,freq_description = st.tabs(["Pie Chart", "Analysis"])

        with freq1_chart:
            self.pie_chart()

        with freq_description:
            st.markdown("""
            - **P2P (Peer-to-Peer)**: :blue[45%] → Almost half of all transactions are direct money transfers between individuals → Suggests strong adoption of digital wallets/UPI for personal use.
            - **P2M (Peer-to-Merchant)**: :blue[35%] → Over one-third of transactions are customer-to-business (e.g., shopping, services) → Indicates digital payments are widely accepted in retail/merchant space.
            - **Bill Payments**: :blue[15%] → Utility payments (electricity, gas, internet) form a significant chunk → Shows that digital platforms are being used for recurring payments.
            - **Recharges**: :blue[5%] → Smallest share; likely because recharge is low-ticket and infrequent compared to daily P2P/P2M.

            - **Customer Behavior — Insight**: Customers mainly use the platform for everyday personal transfers (P2P) and shopping (P2M).
            - **Customer Behavior — Opportunity**: This suggests growth opportunities in merchant onboarding and bill payment automation.

            - **Risk / Fraud — Observation**: Fraud tends to be more prevalent in P2P, since it involves direct transfers without merchant oversight.
            """)

            

    
    def pie_chart(self):
        counts = self.df['type'].value_counts(dropna=False)  # includes NaN if any
        labels = counts.index.astype(str)
        sizes = counts.values

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.pie(sizes, labels=labels, autopct="%.0f%%", startangle=90, counterclock=False)
        ax.axis('equal')  # keep circle
        st.pyplot(fig)

    def top_merchants(self):
        st.subheader("Top Merchant Category",divider=True)
        merchant_tab1, merchant_tab2= st.tabs(["Chart", "Description"])
        with merchant_tab1:
            self.histogram_top_merchants()
        with merchant_tab2:
            st.markdown("""
            - Fraud may concentrate in Shopping (card-not-present frauds, online scams) or Utilities (fake biller accounts).  
            - Categories with low natural spending (e.g., Healthcare, Transport) might also flag suspicious outliers if high-value transactions suddenly appear.
            """)

    
    #histogram for top merchant
    def histogram_top_merchants(self):
        merchant_temp=self.df.groupby(['category'])['amount'].sum().sort_values(ascending=False)
        merchant_tem= pd.DataFrame(merchant_temp)
        fig = plt.figure(figsize=(8, 5))
        sns.barplot(
            merchant_tem,
            x="amount",
            y="category",
            palette="viridis",
            hue="category"
        )

        for index, value in enumerate(merchant_tem["amount"]):
                if index==9 or index==8:
                    plt.text(value - 5_500_000, index, f"₹{value/1e6:.1f}M", va="center", color="white", fontsize=9)
                else:
                    plt.text(value - 7_500_000, index, f"₹{value/1e6:.1f}M", va="center", color="white", fontsize=9)


        plt.title("Total Transaction Amount by Merchant Category", fontsize=12)
        plt.xlabel("Amount (INR)", fontsize=12)
        plt.ylabel("Merchant Category", fontsize=12)
        plt.tight_layout()

            # Show in Streamlit (exact plot, no changes)
        st.pyplot(fig)
                

            


