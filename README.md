
# MacroLens: Economic Event Market Impact Predictor

> Analyze how major economic events historically impacted markets, and predict outcomes of new scenarios using pattern matching and economic theory.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

 **[Live Demo](YOUR_STREAMLIT_URL_HERE)** |**[Methodology](#methodology)**

---

## Overview

MacroLens helps investors, analysts, and researchers understand how markets respond to major economic events. By combining a curated database of 15+ historical crises with economic theory frameworks and similarity-based pattern matching, it provides probabilistic forecasts with uncertainty bands.

## Features

### Event Explorer
Deep-dive into major historical events (2008 GFC, COVID-19, Oil Crises, Fed Policy Shifts) with impact data across 14 asset classes and 5 time horizons.

### Scenario Builder
Input current/hypothetical macro conditions → Find most similar historical events → Get weighted predictions with confidence bands.

### Portfolio Stress Test
Upload your portfolio allocation and see how it would have performed during historical crises.

### Economic Theory Engine
Learn the frameworks (Flight to Quality, Stagflation, Monetary Transmission) behind the predictions.

## Screenshots

[Add screenshots after deployment]

## Tech Stack

- **Frontend/Backend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **ML/Statistics**: scikit-learn, SciPy
- **Visualization**: Plotly
- **Data**: Curated historical database + FRED API (future)

Methodology
1. Historical Event Database
Curated from academic papers, Federal Reserve data, and financial archives. Each event includes:

Pre-event macro conditions (inflation, rates, unemployment, GDP)
Asset performance across 5 time horizons (1M to 2Y)
Severity score, triggers, and narrative description

2. Similarity Engine
Uses weighted Euclidean distance on normalized macro features:
Copysimilarity = 100 * (1 - sqrt(Σ wᵢ * ((xᵢ - yᵢ) / rangeᵢ)² / Σ wᵢ))
3. Impact Aggregation
Similarity-weighted average across matched events with min/max bands representing historical range.
4. Theory Overlay
Maps event categories to applicable economic frameworks (Flight to Quality, Monetary Transmission, etc.) for qualitative context.

Limitations

Historical bias: Past patterns may not repeat
Limited data: Some combinations (e.g., crypto during 1970s) don't exist
Black swans: Unprecedented events by definition
Regime changes: Modern central banks may respond differently

References

Reinhart & Rogoff (2009): This Time Is Different
Dalio (2018): Principles for Navigating Big Debt Crises
Kindleberger (1978): Manias, Panics, and Crashes
Federal Reserve Economic Data (FRED)

License
MIT License - see LICENSE file.

Disclaimer
This tool is for educational and research purposes only. It does not constitute financial advice. Past performance does not guarantee future results. Always consult qualified financial professionals before making investment decisions.

Author
Your Name: Alex Muelas Del Moral
Portfolio: streamlit
Email: alex.muelas6@gmail.com


⭐ If you find this useful, please star the repo!

## Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/macrolens.git
cd macrolens

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
