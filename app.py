import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Streamlit app configuration
st.set_page_config(page_title="Churn Dashboard", layout="wide")
# Modern cover block-inspired CSS
st.markdown("""
    <style>
    .wp-cover-block {
        background: #111;
        min-height: 320px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 48px 0 32px 0;
        border-radius: 0;
        margin-bottom: 32px;
        box-shadow: none;
        position: relative;
        overflow: hidden;
        width: 80vw;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    .wp-cover-block h1 {
        color: #fff;
        font-size: 3.2rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 24px;
        letter-spacing: 1.5px;
        font-family: 'Montserrat', 'Arial Black', Arial, sans-serif;
        line-height: 1.1;
        text-transform: uppercase;
    }
    .wp-cover-block .subtitle {
        color: #bffcff;
        font-size: 1.15rem;
        text-align: center;
        margin-bottom: 32px;
        font-family: 'Fira Mono', 'Consolas', 'Courier New', monospace;
        font-weight: 500;
        letter-spacing: 0.5px;
        background: none;
    }
    .wp-cta-buttons {
        display: flex;
        gap: 18px;
        justify-content: center;
        margin-bottom: 0;
        flex-wrap: wrap;
    }
    .wp-cta-btn {
        background: #1ffcff;
        color: #111 !important;
        font-family: 'Fira Mono', 'Consolas', 'Courier New', monospace;
        font-weight: 700;
        font-size: 1.1rem;
        border: none;
        border-radius: 0;
        padding: 14px 38px;
        text-decoration: none;
        box-shadow: none;
        transition: background 0.2s, color 0.2s;
        display: inline-block;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .wp-cta-btn.secondary {
        background: #111;
        color: #fff !important;
        border: 2px solid #fff;
    }
    .wp-cta-btn:hover {
        background: #fff;
        color: #111 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="wp-cover-block">
    <h1><strong>YOUR DATA.<br>DECODED.<br>DEPLOYED.</strong></h1>
    <div class="subtitle">I can help you translate data into operational clarity and strategic growth.</div>
    <div class="wp-cta-buttons">
        <a class="wp-cta-btn" href="https://tylervportfolio.wordpress.com/services/" target="_blank">EXPLORE CAPABILITIES</a>
        <a class="wp-cta-btn secondary" href="https://tylervportfolio.wordpress.com/lets-talk-data/" target="_blank">BOOK A STRATEGY CALL</a>
    </div>
</div>
""", unsafe_allow_html=True)

# File upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        # Load CSV
        df = pd.read_csv(uploaded_file)
        
        # Validate required columns
        required_columns = ['Churn', 'Contract', 'InternetService', 'PaymentMethod', 'TotalCharges']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Missing required columns. Your CSV must include: {required_columns}")
            st.stop()
        
        # Clean TotalCharges
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)
        
         # Create dashboard
        color_palette = ['#00C9A7', '#845EC2', '#FFC75F', '#FF6F91', '#0081CF', '#F9F871']
        fig = make_subplots(
            rows=2, cols=2, 
            subplot_titles=('Overall Churn', 'Churn by Contract', 'Churn by Internet', 'Churn by Payment'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}], [{'type': 'bar'}, {'type': 'bar'}]]
        )
        # Overall Churn Rate
        churn_rate = df['Churn'].value_counts(normalize=True).get('Yes', 0) * 100
        st.metric("Overall Churn Rate", f"{churn_rate:.2f}%")

        # Total Revenue Lost
        lost_revenue = df[df['Churn'] == 'Yes']['TotalCharges'].sum()
        st.metric("Total Revenue Lost (Churned Customers)", f"${lost_revenue:,.2f}")

        # Top 5 Payment Methods by Churn Rate
        payment_churn_rate = (
            df.groupby('PaymentMethod')['Churn']
            .value_counts(normalize=True)
            .unstack()
            .get('Yes', pd.Series())
            .sort_values(ascending=False)
            .head(5)
)
        st.subheader("Top 5 Payment Methods by Churn Rate")
        st.dataframe(payment_churn_rate.apply(lambda x: f"{x*100:.2f}%"))

        # Overall Churn Rate Pie
        churn_counts = df['Churn'].value_counts(normalize=True) * 100
        fig.add_trace(go.Pie(
            labels=churn_counts.index, 
            values=churn_counts.values, 
            name='Churn Rate', 
            marker=dict(colors=[color_palette[3], color_palette[0]]),
            textinfo='label+percent',
            hole=0.4
        ), row=1, col=1)

        # Churn by Contract
        contract_churn = df.groupby('Contract')['Churn'].value_counts(normalize=True).unstack() * 100
        fig.add_trace(go.Bar(
            x=contract_churn.index, 
            y=contract_churn['Yes'], 
            name='Contract Churn', 
            marker_color=color_palette[1]
        ), row=1, col=2)

        # Churn by Internet Service
        internet_churn = df.groupby('InternetService')['Churn'].value_counts(normalize=True).unstack() * 100
        fig.add_trace(go.Bar(
            x=internet_churn.index, 
            y=internet_churn['Yes'], 
            name='Internet Churn', 
            marker_color=color_palette[2]
        ), row=2, col=1)

        # Churn by Payment Method
        payment_churn = df.groupby('PaymentMethod')['Churn'].value_counts(normalize=True).unstack() * 100
        fig.add_trace(go.Bar(
            x=payment_churn.index, 
            y=payment_churn['Yes'], 
            name='Payment Churn', 
            marker_color=color_palette[4]
        ), row=2, col=2)

        # Customize layout
        fig.update_layout(
            height=650,
            width=1100,
            font=dict(size=13, color='#F5F6FA'),
            plot_bgcolor='#23272F',
            paper_bgcolor='#181C24',
            legend=dict(bgcolor='#181C24', font=dict(color='#F5F6FA')),
            margin=dict(t=60, l=30, r=30, b=30)
        )
                # Add more space between subplot titles and plots
        for annotation in fig['layout']['annotations']:
            annotation['y'] += 0.06  # Increase this value for more space

        # Display dashboard
        st.plotly_chart(fig, use_container_width=True)
        st.success("Dashboard generated! Explore the charts above. See the report for recommendations or schedule a strategy call.")

    except Exception as e:
        st.error(f"Error processing CSV: {e}")
        st.error("Ensure the file is a valid CSV with the required columns. Contact [Your Contact Info] for help.")
else:
    st.info("Please upload a CSV file to generate the dashboard.")