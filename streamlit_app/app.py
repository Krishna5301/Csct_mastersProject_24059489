import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import pickle
import os
import re

# --- CONFIGURATION ---
MODEL_DIR = "../notebooks/saved_models/"
REQUIRED_COLUMNS = [
    "ds", "coicop_code", "volume", "price", "deflator",
    "unemployment_rate", "is_holiday"
]
COICOP_LEGEND = {
    "01": "Food & Non-Alcoholic Beverages",
    "02": "Alcoholic Beverages & Tobacco",
    "03": "Clothing & Footwear",
    "04": "Housing, Water, Electricity, Gas",
    "05": "Furnishings & Routine Household Maintenance",
    "06": "Health",
    "07": "Transport",
    "08": "Communication",
    "09": "Recreation & Culture",
    "10": "Education",
    "11": "Restaurants & Hotels",
    "12": "Miscellaneous Goods & Services"
}

st.set_page_config(
    page_title="UK Retail Demand Forecast App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DARK MODE AND CUSTOM STYLES ---
st.markdown("""
    <style>
    body, .stApp { background-color: #181a1b !important; color: #f5f5f7 !important; }
    .stTextInput, .stFileUploader, .stSelectbox, .stNumberInput, .stSlider, .stButton, .stDownloadButton, .stRadio {
        background-color: #232627 !important;
        color: #f5f5f7 !important;
        border-radius: 10px !important;
        border: 2px solid #444 !important;
        padding: 10px !important;
    }
    .stSlider > div[data-baseweb="slider"] {
        padding: 0 15px !important;
        border-radius: 10px;
        border: 2px solid #444;
        background-color: #232627 !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 16px !important;
        border: 2px solid #444 !important;
        margin-right: 4px !important;
        background-color: #232627 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.header("COICOP Codes 📂")
st.sidebar.dataframe(pd.DataFrame([{"COICOP": k, "Category": v} for k, v in COICOP_LEGEND.items()]), hide_index=True, use_container_width=True)
st.sidebar.markdown("---")
st.sidebar.markdown("""
**How to use:**
- Upload a CSV file with the required columns (see below)
- Forecasts will be generated for each unique COICOP code found
- Set your forecast horizon (2–8 quarters)
- Download results as CSV
""")

# --- MAIN TITLE ---
st.markdown("""
<h1 style='color:#fde047;display:flex;align-items:center;gap:8px;'>📊 UK Retail Demand Forecast App</h1>
""", unsafe_allow_html=True)
st.write("Forecast quarterly UK retail demand by category using pre-trained Prophet models.")

# --- SAMPLE FORMAT ---
with st.expander("📄 Sample CSV Format / Required Columns", expanded=True):
    st.markdown("Your uploaded file **must** have all these columns, no extra or missing:")
    st.code(
        "ds,coicop_code,volume,price,deflator,unemployment_rate,is_holiday\n"
        "2022-01-01,05,18769,11000.0,101.5,4.1,0\n"
        "2022-04-01,05,18700,11120.0,100.9,4.2,0\n"
        "2022-07-01,05,18800,11230.0,101.3,4.0,0",
        language="csv")

# --- FILE UPLOAD ---
st.markdown("### Upload your data file (CSV):")
uploaded_file = st.file_uploader("Select CSV file with required columns", type="csv")

# --- FORECAST HORIZON ---
horizon = st.slider("Forecast horizon (quarters ahead):", min_value=2, max_value=8, value=8)

# --- FUNCTION DEFINITIONS ---
def get_parent_code(coicop_code):
    return str(coicop_code).split(".")[0].zfill(2)

def load_prophet_model(parent_code):
    fname = f"prophet_model_coicop_{parent_code}.pkl"
    fpath = os.path.join(MODEL_DIR, fname)
    if not os.path.exists(fpath):
        return None, f"No Prophet model found for COICOP {parent_code}"
    try:
        with open(fpath, "rb") as f:
            return pickle.load(f), None
    except Exception as e:
        return None, str(e)

def prepare_future_df(df_code, periods):
    last_row = df_code.sort_values("ds").iloc[-1]
    future_dates = pd.date_range(
        start=pd.to_datetime(last_row["ds"]) + pd.offsets.QuarterBegin(),
        periods=periods, freq="Q"
    )
    future_df = pd.DataFrame({"ds": future_dates})
    for col in ["price", "deflator", "unemployment_rate", "is_holiday"]:
        future_df[col] = last_row[col]
    return future_df

# --- FORECAST EXECUTION ---
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, parse_dates=["ds"])
        df = df[REQUIRED_COLUMNS].copy()
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        st.stop()

    df["coicop_code"] = df["coicop_code"].apply(get_parent_code)
    codes_present = sorted(df["coicop_code"].unique())

    tabs = st.tabs([f"COICOP {code} - {COICOP_LEGEND.get(code,'')}" for code in codes_present])
    for i, code in enumerate(codes_present):
        with tabs[i]:
            df_code = df[df["coicop_code"] == code].sort_values("ds").reset_index(drop=True)
            model, err = load_prophet_model(code)
            if model is None:
                st.error(err)
                continue

            future_df = prepare_future_df(df_code, horizon)
            forecast = model.predict(future_df)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=forecast["ds"], y=forecast["yhat"],
                mode="lines+markers", line=dict(color="#fde047", width=3),
                marker=dict(size=8, symbol="circle")
            ))
            fig.update_layout(
                plot_bgcolor="#232528", paper_bgcolor="#232528", font_color="#f5f5f7",
                title=f"Forecasted Volume for COICOP {code}: {COICOP_LEGEND.get(code,'')}",
                xaxis_title="Quarter", yaxis_title="Forecasted Volume (£ millions, chained)",
                showlegend=False, margin=dict(l=35, r=30, t=60, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)

            out_df = forecast[["ds", "yhat"]].rename(columns={"ds": "forecast_quarter", "yhat": "forecast_volume"})
            st.download_button(
                label="⬇️ Download Forecast CSV",
                data=out_df.to_csv(index=False).encode(),
                file_name=f"forecast_coicop_{code}.csv",
                mime="text/csv",
            )
            st.markdown(f"""
                **Insights:**
                Forecast shows projected demand for **{COICOP_LEGEND.get(code, f'COICOP {code}')}**
                over the next **{horizon} quarters** using Prophet trained on macroeconomic features.
            """, unsafe_allow_html=True)
else:
    st.info("Upload a CSV file to start forecasting. Format and column requirements shown above.")
