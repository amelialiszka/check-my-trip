# ✈️ check-my-trip: End-to-End Travel Offer Valuation & Analytics System

**check-my-trip** is an end-to-end machine learning system designed to parse, analyze, and evaluate travel packages from major Polish travel portals (e.g., r.pl). 

By integrating automated web scraping, cloud database storage, domain-specific feature engineering, and a tuned **XGBoost regression model**, the system determines whether a given holiday offer is **fairly priced, overpriced, or an exceptional deal**.

---

## 🏗️ System Architecture

The project is structured into modular, decoupled pipelines:

```text
[ Travel Offer URL ] 
         │
         ▼
 1. LINK COLLECTOR & SCRAPER ──► Parses raw HTML/JSON (hotel, stars, board, price, distance)
         │
         ▼
 2. TURSO CLOUD DATABASE ─────► Persists raw & processed offers via LibSQL
         │
         ▼
 3. FEATURE ENGINEERING (FE 3.4) ► Computes key ratios (stars_x_duration, seasonal flags, keywords)
         │
         ▼
 4. ML ENGINE (XGBoost) ──────► Predicts baseline fair market value (R² = 0.7057)
         │
         ▼
 5. WEB INTERFACE [In Progress]► Renders instant offer evaluation & deal score to the user
```

### Module Breakdown:
1. **Dynamic Web Scraper & Link Collector (Playwright):** Uses Playwright's headless browser automation to render JavaScript-heavy listings, bypass dynamic hydration barriers, and extract structured raw offer payloads (pricing, hotel standards, board types, flight dates).
2. **Storage Layer (`OfferStorage`):** Integration with **Turso Cloud DB** (`libsql_client`) for continuous ingestion and time-series tracking.
3. **Analyzer & Feature Engineer (FE 3.4):** Handles Target Encoding, log-space transformations, seasonal indicators (`is_peak_summer`), and luxury keyword matching.
4. **Machine Learning Model:** A highly regularized single-stage **XGBoost Regressor** trained on continuous prices ($\log(1+y)$), delivering robust generalization on unseen market data.
5. **Web App Interface (Coming Soon):** A web interface allowing users to paste any offer URL and receive an instant valuation report.

---

## 📊 ML Model Performance & Validation

Evaluated on an **unseen, hold-out test set ($X_{test}$)**, the core valuation model avoids error-cascading associated with multi-stage classifiers and demonstrates strong stability:

| Metric | Hold-out Value | Context / Benchmark |
| :--- | :--- | :--- |
| **$R^2$ Score** | **0.7057** | Explains **70.6% of market price variance** across dynamic listings. |
| **Mass-Market MAE ($\le 8\text{k}$ PLN)** | **405.72 PLN** | **$\sim 10\%$ relative error** on standard holiday packages. |
| **Overall MAE** | **514.93 PLN** | Average absolute error across all tested market segments. |

---

## ⚠️ Current Limitations & Active Roadmap

* **Data Scale:** The database currently holds a growing dataset of ~3,000 scraped listings, causing a class imbalance in the extreme luxury segment (>8k PLN).
* **Planned ETL Automation:** Migrating local scraping scripts into automated, scheduled workflows (e.g., GitHub Actions / Apache Airflow).
* **Web Client Deployment:** Finalizing the web app for real-time link parsing and interactive deal evaluation.

---

## 🛠️ Tech Stack

* **Languages & Core:** Python 3.11+, Pandas, NumPy
* **Scraping & Storage:** Playwright, BeautifulSoup4, Requests, LibSQL (`turso`)
* **Machine Learning:** XGBoost, Scikit-Learn, Optuna
* **Frontend/Web:** Streamlit / HTML (Targeting Web Interface)

---

## 👩‍💻 Author
Created as an applied mathematics & ML engineering project.