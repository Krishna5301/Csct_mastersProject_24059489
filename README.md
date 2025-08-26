# UK Retail Demand Forecasting System

This project implements a demand forecasting system for UK retail consumption using Prophet. The system forecasts UK household demand using official ONS consumer trend datasets and includes a Streamlit web application for interactive forecasting and visualization.

## Features

* **Interactive Forecasting:** Use the Streamlit web app to get demand forecasts for different retail categories.
* **Data-driven:** Utilizes official ONS and FRED datasets for accurate forecasting.
* **Robust Methodology:** The development process compared Prophet with ARIMA, LSTM, and XGBoost models to select the best-performing one for the application.
* **Easy to Use:** Simply upload a CSV file with the required historical data to generate a forecast.

## Project Structure

```

UK_Retail_Demand_Forecasting/
├── notebooks/
│   ├── CTCVMSA.xlsx
│   ├── CTIDSA.xlsx
│   ├── CTCPSA.xlsx
│   ├── UKUNRATE.csv
│   ├── saved_models/
│   │   └── prophet_model_coicop_01.pkl
│   └── Model_Development.ipynb
├── app.py
└── README.md

````

## Data Sources

The following official datasets form the foundation of the forecasting system:

* **Consumer Trends: Chained Volume Measures (Seasonally Adjusted)** (`CTCVMSA.xlsx`)
    * **Purpose**: Core input dataset representing real (inflation-adjusted) household consumption volumes across COICOP categories.
    * **Granularity**: Quarterly
* **Consumer Trends: Implied Deflator (Seasonally Adjusted)** (`CTIDSA.xlsx`)
    * **Purpose**: Inflation trend tracking; used as an external regressor.
    * **Granularity**: Quarterly
* **Consumer Trends: Current Price (Seasonally Adjusted)** (`CTCPSA.xlsx`)
    * **Purpose**: Optional dataset for revenue-based forecasting or comparative analysis.
    * **Granularity**: Quarterly

    *You can find the ONS datasets above at the following link:*
    [ONS Consumer Trends Data](https://www.ons.gov.uk/economy/nationalaccounts/satelliteaccounts/bulletins/consumertrends/julytoseptember2024/relateddata)

* **UK Public Holidays (Gov.uk API)**
    * **Purpose**: To model holiday effects using Prophet’s built-in holidays feature.
    * **Link**: [UK Bank Holidays API](https://www.api.gov.uk/gds/bank-holidays/#bank-holidays)

* **UK Unemployment Rate (FRED)** (`UKUNRATE.csv`)
    * **Purpose**: Macroeconomic regressor for demand sensitivity testing.
    * **Granularity**: Quarterly

## Methodology

The forecasting system was developed using the following steps:

1.  **Data Processing:** The system loads and processes the ONS and FRED datasets, merging them to create a comprehensive dataset for modeling.
2.  **Model Development:** Several time series models were developed and benchmarked, including Prophet, ARIMA, LSTM, and XGBoost.
3.  **Model Evaluation:** The models were evaluated using MAPE, MAE, and RMSE metrics. Prophet was chosen as the final model for its performance and interpretability.
4.  **Model Saving:** The trained Prophet model is saved as a `.pkl` file for use in the Streamlit application.

## Getting Started

### Prerequisites

You will need Python 3.x installed. You can create a virtual environment to manage dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
````

### Installation

Install the required Python libraries. You can create a `requirements.txt` file with the following content and install it.

**requirements.txt:**

```
streamlit
pandas
numpy
plotly
scikit-learn
prophet
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

### Running the Application

To run the Streamlit web application, execute the following command in your terminal:

```bash
streamlit run app.py
```

## How to Use the App

1.  Prepare a CSV file containing the historical data. The file must include the columns: `ds`, `coicop_code`, `volume`, `price`, `deflator`, `unemployment_rate`, and `is_holiday`.
2.  Run the Streamlit application using the command above.
3.  Upload your CSV file using the file uploader in the sidebar.
4.  Select the COICOP category you wish to forecast from the dropdown menu.
5.  The application will display the historical data, the forecast plot, and its components. You can also download the forecast data as a new CSV file.


