# ✈️ Check My Trip — AI & ML Travel Price Evaluator

**Check My Trip** is an end-to-end Machine Learning and Generative AI application that evaluates vacation offer prices in real time. By simply pasting a URL of a travel package, the application scrapes the webpage, extracts structured offer parameters using Google Gemini NLP, and predicts a fair market price using an optimized Machine Learning model trained on a **custom-built, real-world dataset**.

## 🌟 Key Features

* 🚀 **Live Cloud Deployment**: The application is successfully deployed and running live on **Streamlit Community Cloud**, handling web scraping, API calls, and ML inference directly in the cloud. [**Check it out live here!**](https://check-my-trip.streamlit.app/)

* 🎯 **Custom Dataset Generation**: I did not use any pre-existing datasets. I built a fully autonomous ETL pipeline (`link_collector.py` + `scraper.py` + `analyzer.py`) to gather, process, and construct my own dataset of travel offers from scratch.

* **Automated Web Scraping**: Powered by **Playwright** (headless Chromium) and **BeautifulSoup4** to extract raw page content, bypassing dynamic JavaScript rendering.

* **LLM Feature Extraction**: Leverages **Google Gemini 3.5 Flash Lite API** to parse unstructured HTML text into strictly formatted JSON attributes (destination, star rating, board type, departure city, duration, actual price).

* **Machine Learning Price Estimation**: Uses an optimized **XGBoost Regressor** model to estimate fair offer values based on historical market trends collected in my custom dataset.

* **Real-time Price Evaluation**: Highlights price differences (overpriced vs. good deal) with custom UI visual indicators in Streamlit.

* **Hybrid Storage Architecture**: Uses **Turso (libSQL)** for cloud-based offer caching with an automatic, resilient offline fallback to local execution.

## 🏗️ Architecture & Data Flow

```text
[ Travel Offer URL ]
        │
        ▼
┌──────────────────┐
│  Playwright      │ ➔ Scrapes raw text & cleans HTML (scraper.py)
└────────┬─────────┘
        │
        ▼
┌──────────────────┐
│  Gemini API      │ ➔ Parses text into structured JSON schema (analyzer.py)
└────────┬─────────┘
        │
        ▼
┌──────────────────┐
│  ML Predictor    │ ➔ Calculates estimated fair price per person (.pkl)
└────────┬─────────┘
        │
        ▼
┌──────────────────┐
│  Streamlit UI    │ ➔ Displays price deal analysis + saves to Turso DB (app.py)
└──────────────────┘
```

## 🛠️ Tech Stack

* **Frontend, Web Framework & Hosting**: [Streamlit](https://streamlit.io/) & Streamlit Community Cloud
* **Scraping**: [Playwright](https://playwright.dev/python/), [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/), RegEx
* **NLP & Information Extraction**: [Google Gemini API](https://ai.google.dev/) (`google-generativeai`)
* **Machine Learning**: [XGBoost](https://xgboost.readthedocs.io/), [Scikit-Learn](https://scikit-learn.org/), Jupyter Notebook
* **Database**: [Turso](https://turso.tech/) (`libsql-client`), CSV Offline Snapshots

## 📁 Repository Structure

```text
check-my-trip/
├── app.py                        # Main Streamlit web application (UI)
├── main.py                       # Orchestration script (Scrapes links from DB -> Analyzes -> Stores)
├── link_collector.py             # Crawler to gather offer URLs into the Turso database
├── scraper.py                    # Playwright web scraper module
├── analyzer.py                   # Gemini NLP information extraction engine
├── storage.py                    # Turso database client (read/write operations)
├── travel_price_predictor.pkl    # Pre-trained ML model artifact
├── travel_price_prediction.ipynb # EDA, Reproducible ML training & tuning notebook
├── offers_dataset.csv            # Custom offline dataset snapshot for model training
├── packages.txt                  # Linux system dependencies for Streamlit Cloud
├── requirements.txt              # Python dependencies
└── .env.example                  # Environment variables template
```

## 🚀 Local Setup & Installation

### Prerequisites

* Python 3.11+ installed
* Git

### Step-by-Step Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/check-my-trip.git
   cd check-my-trip
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and fill in your API credentials:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env`:*
   ```env
   GEMINI_API_KEY="your_google_gemini_api_key"
   TURSO_DATABASE_URL="libsql://your-database.turso.io"
   TURSO_AUTH_TOKEN="your_turso_auth_token"
   ```

5. **(Optional) Run the automated Data Pipeline:**
   If you want to scrape new offers and build your dataset from scratch, you need to execute the pipeline in two steps:

   * **Step 1:** Collect offer URLs and populate the Turso database.
     You must specify the target portal using the `--provider` argument. You can also limit the number of scraped offers using `--limit` (default is 500).

     *Available providers:* `tui`, `wakacje`, `itaka`, `rainbow`, `rainbow_luxury`, `travelplanet`.

     *Example usage:*
     ```bash
     python link_collector.py --provider tui --limit 100
     ```

   * **Step 2:** Process the collected links (Scrape data -> Analyze via LLM -> Store structured results).
     ```bash
     python main.py
     ```

6. **Run the Streamlit application locally:**
   ```bash
   streamlit run app.py
   ```

## 📊 Model Training & Reproducibility

The machine learning workflow is documented in `travel_price_prediction.ipynb`.

1. **Custom Data Collection**: No pre-made datasets were used. The raw data was autonomously scraped, extracted using LLMs, and saved to `offers_dataset.csv` via my custom pipeline orchestrated by `main.py`.
2. **Data Preprocessing**: Handling feature encoding, missing value imputations, and normalization.
3. **Model Evaluation (XGBoost)**: The trained **XGBoost Regressor** demonstrates excellent generalization capabilities. The Mean Absolute Error (MAE) achieved during cross-validation on the training set is closely aligned with the mean MAE on the unseen test set, indicating a robust fit with minimal overfitting.
4. **Reproducibility**: All operations are built to ensure deterministic output evaluation across runs, exporting the final pipeline to `travel_price_predictor.pkl`.

## 🌐 Live Cloud Deployment

This application is successfully deployed and running publicly!

👉 [**Try the Live App on Streamlit Cloud**](https://check-my-trip.streamlit.app/)

To replicate the cloud environment:

* System-level dependencies for headless Chromium (required by Playwright) are handled via `packages.txt`.
* Environment variables (`GEMINI_API_KEY`, `TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`) are securely injected through the **Streamlit Cloud Secrets** manager, meaning end-users don't need to configure any local API keys to test the live app.

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.