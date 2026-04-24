import streamlit as st
import pandas as pd
from src.styles import apply_custom_theme
from src.data_loader import get_asset_classes, ASSET_LABELS, get_categories
from src.similarity_engine import find_similar_events, aggregate_impact_prediction
from src.visualizations import (
    plot_similarity_scores, plot_prediction_with_uncertainty,
    plot_macro_gauge
)
from src.theory_engine import get_relevant_theories
from src.ml_engine import predict_with_ml, compare_models
from src.report_generator import generate_scenario_report

st.set_page_config(page_title="Scenario Builder", page_icon="🔮", layout="wide")
apply_custom_theme()

st.markdown('<div class="section-label">🔮 PREDICTIVE ANALYSIS</div>', unsafe_allow_html=True)
st.markdown("# Scenario Builder")
st.caption("Input macro conditions and discover similar historical precedents with AI-powered predictions")

st.divider()

# Try to fetch live data
try:
    from src.live_data import get_current_macro_snapshot, get_fred_client
    fred_available = get_fred_client() is not None
except:
    fred_available = False

# Input panel
st.markdown("## 📝 Macro Conditions")

col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    if fred_available and st.button("📡 Use Live Data"):
        try:
            snapshot = get_current_macro_snapshot()
            if snapshot.get("inflation"):
                st.session_state["input_inflation"] = snapshot["inflation"]
            if snapshot.get("fed_funds_rate"):
                st.session_state["input_fed_rate"] = snapshot["fed_funds_rate"]
            if snapshot.get("unemployment"):
                st.session_state["input_unemployment"] = snapshot["unemployment"]
            st.success("✅ Loaded current macro data")
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
        key="inflation_input"
    )
with col2:
    fed_rate = st.number_input(
        "Fed Funds Rate (%)",
        min_value=0.0, max_value=20.0,
        value=st.session_state.get("input_fed_rate", 5.25),
        step=0.25,
        key="fed_rate_input"
    )
with col3:
    unemployment = st.number_input(
        "Unemployment (%)",
        min_value=2.0, max_value=15.0,
        value=st.session_state.get("input_unemployment", 4.0),
        step=0.1,
        key="unemployment_input"
    )
with col4:
    gdp_growth = st.number_input(
        "GDP Growth (%)",
        min_value=-10.0, max_value=10.0,
        value=st.session_state.get("input_gdp", 2.0),
        step=0.1,
        key="gdp_input"
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
st.markdown("### 📊 Current Macro Snapshot")
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

# Run analysis
user_conditions = {
    "inflation": inflation,
    "fed_funds_rate": fed_rate,
    "unemployment": unemployment,
    "gdp_growth": gdp_growth
}

if st.button("🔍 Analyze Scenario", use_container_width=True):
    with st.spinner("Analyzing historical patterns..."):
        similar_events = find_similar_events(
            user_conditions,
            event_category=category_filter if category_filter != "All" else None,
            top_n=5
        )
    
    st.session_state["similar_events"] = similar_events
    st.session_state["user_conditions"] = user_conditions
    st.session_state["analysis_done"] = True

if st.session_state.get("analysis_done"):
    similar_events = st.session_state["similar_events"]
    
    st.markdown("## 🎯 Historical Pattern Matches")
    
    # Similarity chart
    st.plotly_chart(plot_similarity_scores(similar_events), use_container_width=True)
    
    # Top match details
    if similar_events:
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
    
    # Asset predictions
    st.markdown("## 📈 Asset Class Predictions")
    
    selected_asset = st.selectbox(
        "Select asset class to analyze",
        options=get_asset_classes(),
        format_func=lambda x: ASSET_LABELS.get(x, x)
    )
    
    tab1, tab2, tab3 = st.tabs(["📊 Prediction", "🤖 ML vs Similarity", "📚 Theory"])
    
    with tab1:
        predictions = aggregate_impact_prediction(similar_events, selected_asset)
        
        if any(predictions[h] for h in predictions):
            fig = plot_prediction_with_uncertainty(predictions, selected_asset)
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary cards
            cols = st.columns(5)
            for i, (horizon, label) in enumerate([("1m", "1 Month"), ("3m", "3 Months"), 
                                                    ("6m", "6 Months"), ("1y", "1 Year"), 
                                                    ("2y", "2 Years")]):
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
            st.warning("Insufficient data for this asset class")
    
    with tab2:
        st.markdown("### 🤖 ML Model vs Historical Similarity")
        st.caption("Compare predictions from two different methodologies")
        
        try:
            comparison = compare_models(user_conditions, selected_asset, 
                                         similar_events, severity, duration)
            
            comp_data = []
            for horizon, values in comparison.items():
                comp_data.append({
                    "Horizon": horizon.upper(),
                    "Similarity Model": values["similarity"],
                    "ML Model": values["ml"]
                })
            
            comp_df = pd.DataFrame(comp_data)
            
            import plotly.graph_objects as go
            from src.styles import get_plotly_layout
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Similarity Model",
                x=comp_df["Horizon"],
                y=comp_df["Similarity Model"],
                marker_color='#00D4FF'
            ))
            fig.add_trace(go.Bar(
                name="ML Model (XGBoost)",
                x=comp_df["Horizon"],
                y=comp_df["ML Model"],
                marker_color='#7C3AED'
            ))
            
            layout = get_plotly_layout(
                title="<b>Model Comparison</b>",
                barmode='group',
                height=400,
                yaxis_title="Predicted Return (%)"
            )
            fig.update_layout(layout)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 When models agree, confidence is higher. Divergence suggests unique scenario characteristics.")
            
        except Exception as e:
            st.warning(f"ML comparison unavailable: {e}")
    
    with tab3:
        # Theory based on top match category
        if similar_events:
            category = similar_events[0]["event"]["category"]
            theories = get_relevant_theories(category)
            
            for theory in theories:
                with st.expander(f"📖 {theory['name']}", expanded=True):
                    st.markdown(f"**{theory['description']}**")
                    st.markdown("**Implications:**")
                    for asset, implication in theory["implications"].items():
                        st.markdown(f"- **{asset.replace('_', ' ').title()}**: {implication}")
    
    # Generate Report
    st.divider()
    st.markdown("## 📄 Export Report")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("Generate a professional PDF report of this analysis for sharing or records.")
    with col2:
        try:
            # Prepare all predictions for report
            all_predictions = {}
            for asset in get_asset_classes()[:8]:
                pred = aggregate_impact_prediction(similar_events, asset)
                all_predictions[ASSET_LABELS[asset]] = pred
            
            pdf_buffer = generate_scenario_report(
                user_conditions=user_conditions,
                similar_events=similar_events,
                predictions_by_asset=all_predictions,
                event_category=category_filter
            )
            
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_buffer,
                file_name=f"macrolens_scenario_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF generation error: {e}")