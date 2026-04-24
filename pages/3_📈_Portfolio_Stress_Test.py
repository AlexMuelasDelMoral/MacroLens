import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data_loader import load_events, load_impacts, get_asset_classes, ASSET_LABELS

st.set_page_config(page_title="Portfolio Stress Test", page_icon="📈", layout="wide")

st.title("📈 Portfolio Stress Test")
st.markdown("Enter your portfolio allocation and see how it would have performed during historical crisis events.")

st.divider()

# Portfolio input
st.header("💼 Your Portfolio")
st.caption("Enter allocation percentages (must sum to 100%)")

# Default allocations
default_allocations = {
    "sp500": 40.0,
    "nasdaq": 10.0,
    "us_10y_yield": 20.0,  # Treasuries proxy
    "gold": 10.0,
    "bitcoin": 5.0,
    "oil": 5.0,
    "emerging_markets": 10.0
}

# Let user select which assets to include
st.markdown("**Select assets in your portfolio:**")
all_assets = get_asset_classes()

selected_assets = st.multiselect(
    "Assets",
    options=all_assets,
    default=list(default_allocations.keys()),
    format_func=lambda x: ASSET_LABELS.get(x, x)
)

# Allocation sliders
allocations = {}
cols = st.columns(3)
for i, asset in enumerate(selected_assets):
    with cols[i % 3]:
        allocations[asset] = st.number_input(
            f"{ASSET_LABELS.get(asset, asset)} (%)",
            min_value=0.0, max_value=100.0,
            value=float(default_allocations.get(asset, 10.0)),
            step=1.0,
            key=f"alloc_{asset}"
        )

total_allocation = sum(allocations.values())

if abs(total_allocation - 100) > 0.1:
    st.warning(f"⚠️ Total allocation: {total_allocation:.1f}% (should be 100%)")
else:
    st.success(f"✅ Total allocation: {total_allocation:.1f}%")

# Portfolio size
portfolio_value = st.number_input("Portfolio Value ($)", 
                                    min_value=1000, value=100000, step=1000)

st.divider()

# Event selection for stress test
st.header("🌪️ Select Stress Test Events")

events = load_events()
impacts = load_impacts()

# Only show events with impact data
available_events = [e for e in events if e["id"] in impacts]

event_names = [f"{e['name']} ({e['year']})" for e in available_events]
selected_event_names = st.multiselect(
    "Choose historical events to stress test against",
    options=event_names,
    default=event_names[:3] if len(event_names) >= 3 else event_names
)

if st.button("🔥 Run Stress Test", type="primary", use_container_width=True):
    if abs(total_allocation - 100) > 0.1:
        st.error("Please ensure allocations sum to 100% before running.")
    elif not selected_event_names:
        st.error("Please select at least one event.")
    else:
        st.divider()
        st.header("📊 Stress Test Results")
        
        # Calculate for each event
        results = []
        for event_name in selected_event_names:
            event = next(e for e in available_events 
                         if f"{e['name']} ({e['year']})" == event_name)
            event_impact = impacts[event["id"]]
            
            for horizon in ["1m", "3m", "6m", "1y", "2y"]:
                portfolio_return = 0
                total_weight = 0
                for asset, alloc in allocations.items():
                    if asset in event_impact:
                        val = event_impact[asset].get(horizon)
                        if val is not None:
                            portfolio_return += (alloc / 100) * val
                            total_weight += alloc / 100
                
                # Normalize if some assets have missing data
                if total_weight > 0:
                    portfolio_return = portfolio_return / total_weight * (total_allocation / 100)
                
                results.append({
                    "Event": event["name"],
                    "Year": event["year"],
                    "Horizon": horizon.upper(),
                    "Return (%)": round(portfolio_return, 2),
                    "Portfolio Value": round(portfolio_value * (1 + portfolio_return / 100), 0),
                    "P&L ($)": round(portfolio_value * portfolio_return / 100, 0)
                })
        
        df = pd.DataFrame(results)
        
        # Chart
        fig = go.Figure()
        for event_name in selected_event_names:
            event = next(e for e in available_events 
                         if f"{e['name']} ({e['year']})" == event_name)
            event_data = df[df["Event"] == event["name"]]
            fig.add_trace(go.Scatter(
                x=event_data["Horizon"],
                y=event_data["Return (%)"],
                mode='lines+markers',
                name=f"{event['name']} ({event['year']})",
                line=dict(width=3),
                marker=dict(size=10)
            ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(
            title="Portfolio Performance Across Historical Crises",
            xaxis_title="Time Horizon",
            yaxis_title="Portfolio Return (%)",
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary table
        st.subheader("📋 Detailed Results")
        
        pivot = df.pivot_table(
            index=["Event", "Year"],
            columns="Horizon",
            values="Return (%)",
            aggfunc='first'
        ).reset_index()
        
        st.dataframe(
            pivot,
            hide_index=True,
            use_container_width=True,
            column_config={col: st.column_config.NumberColumn(format="%.1f%%") 
                           for col in pivot.columns if col not in ["Event", "Year"]}
        )
        
        # Worst case scenario
        st.subheader("🚨 Worst Case Scenario")
        worst = df.loc[df["Return (%)"].idxmin()]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Event", f"{worst['Event']} ({worst['Year']})")
        col2.metric("Horizon", worst["Horizon"])
        col3.metric("Loss", f"{worst['Return (%)']:+.1f}%", 
                     delta=f"${worst['P&L ($)']:+,.0f}")
        
        # Portfolio allocation visualization
        st.subheader("🥧 Your Portfolio Allocation")
        alloc_fig = go.Figure(data=[go.Pie(
            labels=[ASSET_LABELS.get(k, k) for k in allocations.keys()],
            values=list(allocations.values()),
            hole=0.4
        )])
        alloc_fig.update_layout(height=400)
        st.plotly_chart(alloc_fig, use_container_width=True)

st.divider()
st.info("💡 **Tip:** Diversification across uncorrelated assets (stocks, bonds, gold, alternatives) historically reduces drawdowns during crises.")
