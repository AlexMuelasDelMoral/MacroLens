import streamlit as st
import pandas as pd
from src.styles import apply_custom_theme
from src.data_loader import (
    get_asset_classes, ASSET_LABELS, ASSET_CATEGORIES, get_categories
)
from src.similarity_engine import find_similar_events, aggregate_impact_prediction
from src.visualizations import (
    plot_similarity_scores, plot_prediction_with_uncertainty, plot_macro_gauge
)
from src.theory_engine import get_relevant_theories

# Optional imports (fail gracefully if modules not present)
try:
    from src.ml_engine import compare_models
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    from src.report_generator import generate_scenario_report
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from src.live_data import get_current_macro_snapshot, get_fred_client
    FRED_AVAILABLE = get_fred_client() is not None
except Exception:
    FRED_AVAILABLE = False


st.set_page_config(page_title="Scenario Builder", page_icon=None, layout="wide")
apply_custom_theme()

st.markdown('<div class="section-label">PREDICTIVE ANALYSIS</div>', unsafe_allow_html=True)
st.markdown("# Scenario Builder")
st.caption("Input macro conditions and discover similar historical precedents")

st.divider()

# ============ MACRO INPUT PANEL ============
st.markdown("## Macro Conditions")

if FRED_AVAILABLE:
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("Load Live Data", use_container_width=True):
            try:
                snapshot = get_current_macro_snapshot()
                if snapshot.get("inflation"):
                    st.session_state["input_inflation"] = snapshot["inflation"]
                if snapshot.get("fed_funds_rate"):
                    st.session_state["input_fed_rate"] = snapshot["fed_funds_rate"]
                if snapshot.get("unemployment"):
                    st.session_state["input_unemployment"] = snapshot["unemployment"]
                st.success("Loaded current macro data")
                st.rerun()
            except Exception as e:
                st.error(f"Could not load live data: {e}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    inflation = st.number_input(
        "Inflation Rate (%)",
        min_value=-5.0, max_value=25.0,
        value=st.session_state.get("input_inflation", 3.5),
        step=0.1,
    )
with col2:
    fed_rate = st.number_input(
        "Fed Funds Rate (%)",
        min_value=0.0, max_value=20.0,
        value=st.session_state.get("input_fed_rate", 5.25),
        step=0.25,
    )
with col3:
    unemployment = st.number_input(
        "Unemployment (%)",
        min_value=2.0, max_value=15.0,
        value=st.session_state.get("input_unemployment", 4.0),
        step=0.1,
    )
with col4:
    gdp_growth = st.number_input(
        "GDP Growth (%)",
        min_value=-10.0, max_value=10.0,
        value=st.session_state.get("input_gdp", 2.0),
        step=0.1,
    )

# Event characteristics
col1, col2, col3 = st.columns(3)
with col1:
    category_filter = st.selectbox(
        "Event Category",
        options=["All"] + get_categories()
    )
with col2:
    severity = st.slider("Event Severity", 1, 10, 7,
                         help="1 = minor, 10 = systemic crisis")
with col3:
    duration = st.slider("Duration (months)", 1, 36, 6)

# Macro gauges
st.markdown("### Current Macro Snapshot")
cols = st.columns(4)
with cols[0]:
    st.plotly_chart(
        plot_macro_gauge(inflation, "Inflation", 0, 15, 2, 6),
        use_container_width=True
    )
with cols[1]:
    st.plotly_chart(
        plot_macro_gauge(fed_rate, "Fed Rate", 0, 20, 2, 8),
        use_container_width=True
    )
with cols[2]:
    st.plotly_chart(
        plot_macro_gauge(unemployment, "Unemployment", 0, 15, 4, 7),
        use_container_width=True
    )
with cols[3]:
    st.plotly_chart(
        plot_macro_gauge(gdp_growth, "GDP Growth", -5, 8, 0, 3),
        use_container_width=True
    )

st.divider()

# ============ RUN ANALYSIS ============
user_conditions = {
    "inflation": inflation,
    "fed_funds_rate": fed_rate,
    "unemployment": unemployment,
    "gdp_growth": gdp_growth,
}

if st.button("Analyze Scenario", use_container_width=True, type="primary"):
    with st.spinner("Analyzing historical patterns..."):
        similar_events = find_similar_events(
            user_conditions,
            event_category=category_filter if category_filter != "All" else None,
            top_n=5,
        )
    st.session_state["similar_events"] = similar_events
    st.session_state["user_conditions"] = user_conditions
    st.session_state["analysis_done"] = True


# ============ DISPLAY RESULTS ============
if st.session_state.get("analysis_done"):
    similar_events = st.session_state["similar_events"]

    if not similar_events:
        st.warning("No similar events found. Try adjusting filters.")
        st.stop()

    st.markdown("## Historical Pattern Matches")
    st.plotly_chart(plot_similarity_scores(similar_events), use_container_width=True)

    # Top match card
    top = similar_events[0]
    st.markdown(f"""
    <div class="glass-card" style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%); border-color: rgba(0, 212, 255, 0.3);">
        <div style="color: #00D4FF; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em;">TOP MATCH</div>
        <h3 style="margin: 0.5rem 0; color: #E4E8F1;">{top['event']['name']} ({top['event']['year']})</h3>
        <div style="color: #8B92B0;">{top['event']['description']}</div>
        <div style="margin-top: 1rem;">
            <span style="color: #00D4FF; font-family: JetBrains Mono; font-size: 2rem; font-weight: 700;">{top['similarity']}%</span>
            <span style="color: #8B92B0; font-size: 0.9rem;"> similarity</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ============ ASSET PREDICTIONS ============
    st.markdown("## Asset Class Predictions")

    col1, col2 = st.columns([1, 2])
    with col1:
        selected_category = st.selectbox(
            "Asset Category",
            options=list(ASSET_CATEGORIES.keys())
        )
    with col2:
        category_assets = ASSET_CATEGORIES[selected_category]
        selected_asset = st.selectbox(
            "Asset Class",
            options=list(category_assets.keys()),
            format_func=lambda x: category_assets[x]
        )

    tab1, tab2, tab3 = st.tabs(["Prediction", "Model Comparison", "Theory"])

    with tab1:
        # BUG FIX: Pass similar_events (the variable) not find_similar_events (the function)
        predictions = aggregate_impact_prediction(similar_events, selected_asset)

        if predictions and any(predictions.get(h) for h in predictions):
            fig = plot_prediction_with_uncertainty(predictions, selected_asset)
            st.plotly_chart(fig, use_container_width=True)

            # Summary cards
            cols = st.columns(5)
            horizon_labels = [
                ("1m", "1 Month"), ("3m", "3 Months"),
                ("6m", "6 Months"), ("1y", "1 Year"), ("2y", "2 Years"),
            ]
            for i, (horizon, label) in enumerate(horizon_labels):
                pred = predictions.get(horizon)
                with cols[i]:
                    if pred:
                        val = pred["expected"]
                        color = "#00F5A0" if val > 0 else "#FF3B6B"
                        st.markdown(f"""
                        <div class="glass-card" style="text-align: center;">
                            <div style="color: #8B92B0; font-size: 0.7rem; letter-spacing: 0.1em;">{label}</div>
                            <div style="color: {color}; font-family: JetBrains Mono; font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">
                                {val:+.1f}%
                            </div>
                            <div style="color: #5A6182; font-size: 0.7rem;">
                                Range: {pred['min']:+.1f} to {pred['max']:+.1f}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="glass-card" style="text-align: center;">
                            <div style="color: #8B92B0; font-size: 0.7rem;">{label}</div>
                            <div style="color: #5A6182;">N/A</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("Insufficient data for this asset class. Try a different one.")

    with tab2:
        st.markdown("### Similarity Model vs Machine Learning")
        st.caption("Compare two different prediction methodologies")

        if not ML_AVAILABLE:
            st.info("ML engine not available. Install xgboost and create src/ml_engine.py")
        else:
            try:
                comparison = compare_models(
                    user_conditions, selected_asset,
                    similar_events, severity, duration
                )

                comp_data = []
                for horizon, values in comparison.items():
                    comp_data.append({
                        "Horizon": horizon.upper(),
                        "Similarity Model": values.get("similarity"),
                        "ML Model": values.get("ml"),
                    })

                comp_df = pd.DataFrame(comp_data)

                import plotly.graph_objects as go
                from src.styles import get_plotly_layout

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name="Similarity Model",
                    x=comp_df["Horizon"],
                    y=comp_df["Similarity Model"],
                    marker_color='#00D4FF',
                ))
                fig.add_trace(go.Bar(
                    name="ML Model",
                    x=comp_df["Horizon"],
                    y=comp_df["ML Model"],
                    marker_color='#7C3AED',
                ))

                layout = get_plotly_layout(
                    title="<b>Model Comparison</b>",
                    barmode='group',
                    height=400,
                    yaxis_title="Predicted Return (%)",
                )
                fig.update_layout(layout)
                st.plotly_chart(fig, use_container_width=True)

                st.info("When models agree, confidence is higher. Divergence suggests unique scenario characteristics.")

            except Exception as e:
                st.warning(f"Model comparison unavailable: {e}")

    with tab3:
        if similar_events:
            category = similar_events[0]["event"]["category"]
            theories = get_relevant_theories(category)

            if not theories:
                st.info(f"No specific theory mappings for category: {category}")

            for theory in theories:
                with st.expander(theory['name'], expanded=True):
                    st.markdown(f"**{theory['description']}**")
                    st.markdown("**Implications:**")
                    for asset, implication in theory["implications"].items():
                        label = asset.replace('_', ' ').title()
                        st.markdown(f"- **{label}**: {implication}")

    # ============ EXPORT REPORT ============
    st.divider()
    st.markdown("## Export Report")

    if not PDF_AVAILABLE:
        st.info("PDF export not available. Install reportlab: `pip install reportlab`")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Generate a professional PDF report of this analysis.")
        with col2:
            try:
                all_predictions = {}
                for asset_id in list(ASSET_LABELS.keys())[:10]:
                    pred = aggregate_impact_prediction(similar_events, asset_id)
                    all_predictions[ASSET_LABELS[asset_id]] = pred

                pdf_buffer = generate_scenario_report(
                    user_conditions=user_conditions,
                    similar_events=similar_events,
                    predictions_by_asset=all_predictions,
                    event_category=category_filter,
                )

                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer,
                    file_name=f"macrolens_scenario_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF generation error: {e}")