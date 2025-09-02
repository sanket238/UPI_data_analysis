import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import matplotlib as mpl



class Demographic:
    
    def __init__(self,data):
        self.df= data
        self.visualize()
    


    def visualize(self):

        demo_col1, demo_col2= st.columns(2)

        with demo_col1:
            #columns 1
            self.age_group()
        with demo_col2:
            #column 2
            self.cross_tab()

        self.heatmap()

        


    def heatmap(self):
       
        st.subheader("State-wise amount heatmap", divider=True)

        tab1, tab2= st.tabs(["HeatMap","Description"])

        with tab1:
            state_amounts = self.df.groupby("sender_state")["amount"].sum().sort_values(ascending=False)

            # Ensure Series
            if isinstance(state_amounts, pd.Series):
                s = state_amounts.copy()
            else:
                s = pd.Series(dtype=float)

            # 1) Vertical heatmap (states as rows)
            vals = s.to_frame(name="Amount")

            # Create a same-shaped array of formatted labels in millions
            annot_labels = (vals["Amount"] / 1e6).map(lambda x: f"{x:.1f}M").to_numpy().reshape(-1, 1)

            cmap = sns.color_palette("BuGn", as_cmap=True)  # or "Blues", "YlOrBr"
            vmin, vmax = float(vals.values.min()), float(vals.values.max())
            norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
            fig1, ax1 = plt.subplots(figsize=(10, max(6, 0.35 * len(vals))))   # adjust height if many states, e.g., (10, 10)

            sns.heatmap(
                vals,                      # numeric data
                cmap="YlGnBu",
                cbar=True,
                annot=annot_labels,        # string annotations
                fmt="",                    # don't reformat strings
                annot_kws={"color": "black", "fontsize": 9, "fontweight": "bold"},
                linewidths=0.5,
                linecolor="white",
                vmin=vmin, vmax=vmax,
                ax=ax1
            )
            for text, value in zip(ax1.texts, vals.values.ravel()):
                # value -> [0,1] scale
                tone = norm(value)
                # choose text color based on background lightness threshold
                text.set_color("white" if tone > 0.55 else "black")

            ax1.set_title("State-wise Amount (Vertical Heatmap)")
            ax1.set_xlabel("")
            ax1.set_ylabel("Sender State")
            ax1.tick_params(axis="y", labelsize=10)
            ax1.tick_params(axis="x", labelsize=10)
            plt.tight_layout()
            st.pyplot(fig1)
        
        with tab2:

            st.markdown("""
            - **High-Value States (Potential Fraud Hotspots)**  
                - States like :blue[**Maharashtra**], :blue[**Uttar Pradesh**], and :blue[**Karnataka**] have the highest transaction volumes (₹49M+, ₹40M+, ₹38M+).  
                - These should be :blue[**priority regions for fraud detection**] since fraudsters usually target areas with dense financial activity.  
                - A single large suspicious transaction in these states may get hidden among genuine traffic → requires :blue[**advanced anomaly detection**].

            - **Urban vs Semi-Urban Dynamics**  
                - :blue[**Delhi**], :blue[**Telangana**], and :blue[**Tamil Nadu**] are strong contributors despite smaller geographic sizes.  
                - High concentration of digital users (e.g., metro areas) means higher chance of :blue[**phishing, account takeover, or synthetic ID fraud**].  
                - Monitoring :blue[**patterns of merchant usage (P2M, Shopping, Utilities)**] here is critical.

            - **Emerging Risk Zones**  
                - States like :blue[**Rajasthan**], :blue[**Gujarat**], :blue[**Andhra Pradesh**], and :blue[**West Bengal**] are in the mid-range transaction volumes (~₹26M).  
                - Sudden spikes in these states can signal :blue[**organized fraud rings**] exploiting less-mature fraud controls compared to larger metro states.
                """)

            st.markdown("""
            **Summary Statement for Business Meeting:**  
            *"Our analysis shows that :blue[**Maharashtra**], :blue[**UP**], and :blue[**Karnataka**] drive the largest share of transactions, making them both revenue hubs and potential fraud hotspots. Metro regions like :blue[**Delhi**] and :blue[**Telangana**] show disproportionately high activity, where fraudsters can blend in easily. Meanwhile, mid-volume states like :blue[**Rajasthan**] and :blue[**Gujarat**] must be closely tracked for unusual spikes, as fraud rings often target emerging digital markets."*
            """)

                



    def age_group(self):
        st.subheader("Age Group Counts", divider=True)
        tab1, tab2 = st.tabs(["Chart", "Description"])
        
        with tab1:
            fig = plt.figure(figsize=(8, 4))
            sns.countplot(
                x=self.df['age_group'],
                order=self.df['age_group'].value_counts().index
            )

            plt.xlabel("Age Group")
            plt.ylabel("Count")
            plt.tight_layout()

            st.pyplot(fig)
        
        with tab2:
            st.markdown("""
            - The majority of transactions are initiated by senders in the :blue-background[26–35] age group, followed by :blue-background[36–45].  
            - Younger senders :blue-background[18–25] also contribute significantly, indicating that risky behavior can involve relatively new or inexperienced account holders.  
            - In contrast, older age groups :blue-background[46–55] and :blue-background[56+] account for far fewer transactions.  
            - The core customer base driving transactions is between :blue-background[26–45], which aligns with the prime working-age segment.  
            - Since fraudsters often exploit younger individuals :blue-background[18–25] as mule accounts, this group requires closer monitoring despite contributing fewer transactions than :blue-background[26–35].  
            - Elderly groups :blue-background[56+] are fewer in number but may be more vulnerable to scams—so while their volume is low, the risk impact can be high.  
            """)
        
    
    #cross tab 
    def cross_tab(self):
        crosstab=pd.crosstab(self.df['age_group'],self.df['category'],values=self.df['amount'],aggfunc="sum",normalize="index")*100
        st.subheader("Cross tab- Age group and Transcation type", divider=True)

        tab1, tab2 = st.tabs(["Chart", "Description"])
        
        with tab1:
          # Ensure rows are in desired order (optional)
            age_groups = list(crosstab.index)
            tx_types = list(crosstab.columns)

            # Convert to tidy format
            long_df = crosstab.reset_index().melt(id_vars=crosstab.index.name or "index",
                                                var_name="Transaction Type",
                                                value_name="Value")
            if crosstab.index.name is None:
                long_df = long_df.rename(columns={"index": "Sender Age Group"})
            else:
                long_df = long_df.rename(columns={crosstab.index.name: "Sender Age Group"})

            # Prepare colors from tab20
            cmap = get_cmap("tab20")
            colors = {tt: cmap(i % cmap.N) for i, tt in enumerate(tx_types)}

            # Build stacked horizontal bars using Matplotlib with Seaborn theme
            sns.set_theme(style="whitegrid")

            fig, ax = plt.subplots(figsize=(8, 4))

            # For each age group, stack categories along x
            y_positions = np.arange(len(age_groups))
            bar_bottoms = np.zeros(len(age_groups))

            for tt in tx_types:
                vals = crosstab[tt].values
                ax.barh(y_positions, vals, left=bar_bottoms, color=colors[tt], label=tt)
                bar_bottoms += vals

            # Axes formatting
            ax.set_yticks(y_positions)
            ax.set_yticklabels(age_groups)
            ax.set_xlabel("Percentage of Transactions")
            ax.set_ylabel("Sender Age Group")
            ax.set_title("Transaction Type Distribution by Sender Age Group", fontsize=14)

            # Legend placement similar to bbox_to_anchor=(1.05, 1), loc='upper left'
            leg = ax.legend(title="Transaction Type", bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()

            st.pyplot(fig)
        
        with tab2:
            st.markdown("""
            **Shopping & Utilities dominate across all age groups**
            - The biggest portion of spend (grey + light blue) is consistently Shopping and Utility payments across all age groups.  
            - This indicates core digital payment usage is still for essentials (bills, household shopping).  

            **Younger age groups spend more on discretionary categories**
            - :blue-background[18–25], :blue-background[26–35] show a higher share of Food, Entertainment, and Recharge compared to older groups.  
            - Suggests youth are early adopters of lifestyle transactions, creating opportunities for partnerships with entertainment and food brands.  

            **Mid-age groups lean towards essentials**
            - :blue-background[36–45], :blue-background[46–55] show strong shares in Groceries, Fuel, and Utilities.  
            - Indicates this segment values convenience and necessity-based spending — good targets for loyalty programs on fuel, grocery, or bill payments.  

            **Older group shows more balance**
            - :blue-background[56+] still spends heavily on utilities and shopping, but also shows a higher proportion in healthcare compared to younger groups.  
            - This signals scope for healthcare partnerships (insurance, medicine delivery, health checkups).  
            """)



        