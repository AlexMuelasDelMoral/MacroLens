import streamlit as st
import pandas as pd
from src.data_loader import get_asset_classes, ASSET_LABELS, get_categories
from src.similarity_engine import find_similar_events, aggregate_impact_prediction
from src.visualizations import plot_similarity_scores, plot_prediction_with_uncertainty
from src.theory_engine import get_relevant_theories

st.set_page_config(page_title="Scenario Builder", page_icon="🔮", layout="wide")

st.title("🔮 Scenario Builder")
st.markdown("Input current/hypothetical macro conditions and find similar historical precedents.")

st.divider()

# Input panel
st.header("📝 Set Macro Conditions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    inflation = st.number_input("Inflation Rate (%)", 
                                  min_value=-5.0, max_value=25.0, 
                                  value=3.5, step=0.1)
with col2:
    fed_rate = st.number_input("Fed Funds Rate (%)", 
                                min_value=0.0, max_value=20.0, 
                                value=5.25, step=0.25)
with col3:
    unemployment = st.number_input("Unemployment (%)", 
                                    min_value=2.0, max_value=15.0, 
                                    value=4.0, step=0.1)
with col4:
    gdp_growth = st.number_input("GDP Growth (%)", 
                                   min_value=-10.0, max_value=10.0, 
                                   value=2.0, step=0.1)

# Filters
col1, col2 = st.columns(2)
with col1:
    category_filter = st.selectbox(
        "Event Category (optional)",
        options=["All"] + get_categories()
    )
with col2:
    top_n = st.slider("Number of similar events", 3, 10, 5)

# Run analysis
if st.button("🔍 Analyze Scenario", type="primary", use_container_width=True):
    user_conditions = {
        "inflation": inflation,
        "fed_funds_rate": fed_rate,
        "unemployment": unemployment,
        "gdp_growth": gdp_growth
    }
    
    # Store in session state
    st.session_state["user_conditions"] = user_conditions
    st.session_state["category_filter"] = category_filter
    st.session_state["top_n"] = top_n
    st.session_state["analyzed"] = True

if st.session_state.get("analyzed", False):
    user_conditions = st.session_state["user_conditions"]
    category_filter = st.session_state["category_filter"]
    top_n = st.session_state["top_n"]
    
    similar_events = find_similar_events(user_conditions, category_filter, top_n)
    
    st.divider()
    st.header("🎯 Analysis Results")
    
    # Similarity scores
    st.subheader("Most Similar Historical Events")
    sim_chart = plot_similarity_scores(similar_events)
    st.plotly_chart(sim_chart, use_container_width=True)
    
    # Detail cards for top matches
    st.subheader("📋 Top Matches Details")
    
    for i, item in enumerate(similar_events[:3]):
        event = item["event"]
        sim = item["similarity"]
        
        with st.expander(f"#{i+1} — {event['name']} ({event['year']}) — Similarity: {sim}%"):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Category", event["category"])
                st.metric("Severity", f"{event['severity']}/10")
                st.metric("Duration", f"{event['duration_months']}mo")
            with col2:
                st.markdown(f"**Description:** {event['description']}")
                st.markdown("**Macro Comparison:**")
                
                pre = event["pre_conditions"]
                comp_df = pd.DataFrame({
                    "Metric": ["Inflation", "Fed Rate", "Unemployment", "GDP Growth"],
                    "Historical": [
                        f"{pre.get('inflation', 'N/A')}%",
                        f"{pre.get('fed_funds_rate', 'N/A')}%",
                        f"{pre.get('unemployment', 'N/A')}%",
                        f"{pre.get('gdp_growth', 'N/A')}%"
                    ],
                    "Your Scenario": [
                        f"{user_conditions['inflation']}%",
                        f"{user_conditions['fed_funds_rate']}%",
                        f"{user_conditions['unemployment']}%",
                        f"{user_conditions['gdp_growth']}%"
                    ]
                })
                st.dataframe(comp_df, hide_index=True, use_container_width=True)
    
    st.divider()
    
    # Asset predictions
    st.header("💹 Predicted Market Impact")
    st.caption("Weighted average based on similarity scores with historical range shown as uncertainty band")
    
    selected_asset = st.selectbox(
        "Select asset class to analyze",
        options=get_asset_classes(),
        format_func=lambda x: ASSET_LABELS.get(x, x)
    )
    
    predictions = aggregate_impact_prediction(similar_events, selected_asset)
    
    # Check if we have valid predictions
    valid_predictions = {k: v for k, v in predictions.items() if v is not None}
    
    if valid_predictions:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = plot_prediction_with_uncertainty(predictions, selected_asset)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Summary Table")
            summary_data = []
            for horizon, pred in predictions.items():
                if pred:
                    summary_data.append({
                        "Horizon": horizon.upper(),
                        "Expected": f"{pred['expected']:+.1f}%",
                        "Range": f"{pred['min']:+.1f}% to {pred['max']:+.1f}%",
                        "N": pred["n_samples"]
                    })
            st.dataframe(pd.DataFrame(summary_data), hide_index=True, use_container_width=True)
        
        # All assets summary
        st.subheader("📊 All Asset Classes - Expected 6M Impact")
        all_assets_data = []
        for asset in get_asset_classes():
            preds = aggregate_impact_prediction(similar_events, asset)
            if preds.get("6m"):
                all_assets_data.append({
                    "Asset": ASSET_LABELS.get(asset, asset),
                    "Expected": preds["6m"]["expected"],
                    "Min": preds["6m"]["min"],
                    "Max": preds["6m"]["max"],
                    "Samples": preds["6m"]["n_samples"]
                })
        
        if all_assets_data:
            df = pd.DataFrame(all_assets_data).sort_values("Expected")
            st.dataframe(
                df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Expected": st.column_config.NumberColumn("Expected (%)", format="%.1f%%"),
                    "Min": st.column_config.NumberColumn("Min (%)", format="%.1f%%"),
                    "Max": st.column_config.NumberColumn("Max (%)", format="%.1f%%")
                }
            )
    else:
        st.warning("Not enough historical data for this asset. Try another asset class or broader filter.")
    
    st.divider()
    
    # Relevant theory
    st.header("📚 Theoretical Framework")
    
    # Get theories from top matched categories
    top_categories = list(set([item["event"]["category"] for item in similar_events[:3]]))
    
    for cat in top_categories:
        theories = get_relevant_theories(cat)
        for theory in theories:
            with st.expander(f"📖 {theory['name']} ({cat})"):
                st.markdown(f"**{theory['description']}**")
                for asset, implication in theory["implications"].items():
                    st.markdown(f"- **{asset.replace('_', ' ').title()}**: {implication}")
else:
    st.info("👆 Set your macro conditions above and click 'Analyze Scenario' to see results.")
