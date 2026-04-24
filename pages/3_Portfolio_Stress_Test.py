import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.styles import apply_custom_theme, get_plotly_layout
from src.data_loader import load_events, load_impacts, ASSET_LABELS
from src.visualizations import plot_portfolio_performance
from src.report_generator import generate_portfolio_report

st.set_page_config(page_title="Portfolio Stress Test", page_icon="📈", layout="wide")
apply_custom_theme()

st.markdown('<div class="section-label">STRESS TESTING</div>', unsafe_allow_html=True)
st.markdown("# Portfolio Stress Test")
st.caption("Simulate your portfolio's behavior under historical crisis scenarios")

st.divider()

# Portfolio Builder
st.markdown("## Build Your Portfolio")
st.caption("Allocate your portfolio across asset classes (must sum to 100%)")

# Preset portfolios
preset = st.selectbox(
    "📋 Start with a preset or build custom",
    ["Custom", "60/40 Classic", "Aggressive Growth", "Permanent Portfolio", "All-Weather (Ray Dalio)"],
    help="Select a preset to auto-populate, then adjust"
)

# Preset definitions
presets = {
    "60/40 Classic": {"sp500": 60, "corporate_bonds_ig": 40},
    "Aggressive Growth": {"sp500": 40, "nasdaq": 30, "tech": 20, "emerging_markets": 10},
    "Permanent Portfolio": {"sp500": 25, "us_10y_yield": 25, "gold": 25, "corporate_bonds_ig": 25},
    "All-Weather (Ray Dalio)": {"sp500": 30, "us_10y_yield": 40, "gold": 15, "basic_materials": 7.5, "corporate_bonds_ig": 7.5},
}

assets_ordered = [
    "sp500", "nasdaq", "tech", "oil", "gold",
    "bitcoin", "emerging_markets", "luxury", "basic_materials",
    "us_10y_yield", "us_2y_yield", "corporate_bonds_ig", "high_yield_bonds"
]

col1, col2, col3 = st.columns(3)
portfolio = {}

for i, asset in enumerate(assets_ordered):
    default_val = presets.get(preset, {}).get(asset, 0)
    col = [col1, col2, col3][i % 3]
    with col:
        portfolio[asset] = st.number_input(
            ASSET_LABELS[asset],
            min_value=0.0, max_value=100.0,
            value=float(default_val),
            step=5.0,
            key=f"port_{asset}"
        )

total = sum(portfolio.values())

# Show allocation status
if abs(total - 100) > 0.1:
    st.warning(f"Portfolio allocation: {total}% (should be 100%)")
else:
    st.success(f"Portfolio allocation: {total}%")

# Portfolio composition pie chart
if total > 0:
    active_portfolio = {k: v for k, v in portfolio.items() if v > 0}
    fig = go.Figure(data=[go.Pie(
        labels=[ASSET_LABELS[k] for k in active_portfolio.keys()],
        values=list(active_portfolio.values()),
        hole=0.6,
        marker=dict(
            colors=['#00D4FF', '#7C3AED', '#00F5A0', '#FFB547', '#FF3B6B', 
                     '#0066FF', '#FF6B00', '#A78BFA', '#06B6D4', '#F472B6'],
            line=dict(color='#0A0E27', width=2)
        ),
        textfont=dict(color='#E4E8F1', size=11),
        textposition='outside'
    )])
    
    layout = get_plotly_layout(
        title="<b>Portfolio Allocation</b>",
        height=400,
        showlegend=True
    )
    layout['annotations'] = [dict(
        text=f'<b>{total:.0f}%</b><br><span style="font-size:12px;color:#8B92B0">Allocated</span>',
        x=0.5, y=0.5, font_size=24, showarrow=False,
        font=dict(color='#00D4FF')
    )]
    fig.update_layout(layout)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Stress Test
st.markdown("## Select Stress Test Scenarios")

events = load_events()
impacts = load_impacts()

event_options = {f"{e['name']} ({e['year']})": e['id'] for e in events if e['id'] in impacts}
selected_events = st.multiselect(
    "Choose crisis scenarios to test",
    options=list(event_options.keys()),
    default=list(event_options.keys())[:3] if event_options else []
)

if st.button("Run Stress Test", use_container_width=True):
    if abs(total - 100) > 0.1:
        st.error("Portfolio must sum to 100% before running stress test")
    elif not selected_events:
        st.error("Please select at least one scenario")
    else:
        st.divider()
        st.markdown("## Stress Test Results")
        
        results = []
        
        for event_display_name in selected_events:
            event_id = event_options[event_display_name]
            event_impacts = impacts.get(event_id, {})
            
            for horizon in ["1m", "3m", "6m", "1y", "2y"]:
                weighted_return = 0
                valid = True
                
                for asset, weight in portfolio.items():
                    if weight == 0:
                        continue
                    if asset not in event_impacts:
                        continue
                    asset_return = event_impacts[asset].get(horizon)
                    if asset_return is None:
                        continue
                    weighted_return += (weight / 100) * asset_return
                
                results.append({
                    "Event Full": event_display_name,
                    "Horizon": horizon.upper(),
                    "Return (%)": round(weighted_return, 2)
                })
        
        results_df = pd.DataFrame(results)
        
        # Performance chart
        fig = plot_portfolio_performance(results_df, selected_events)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary cards
        st.markdown("### Scenario Summary")
        
        cols = st.columns(len(selected_events))
        for i, event_name in enumerate(selected_events):
            event_data = results_df[results_df["Event Full"] == event_name]
            worst = event_data["Return (%)"].min()
            best = event_data["Return (%)"].max()
            avg = event_data["Return (%)"].mean()
            
            with cols[i]:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="color: #00D4FF; font-weight: 700; font-size: 0.9rem; margin-bottom: 0.5rem;">
                        {event_name}
                    </div>
                    <div style="color: {'#FF3B6B' if worst < 0 else '#00F5A0'}; font-family: 'JetBrains Mono'; font-size: 1.5rem; font-weight: 700;">
                        {worst:+.1f}%
                    </div>
                    <div style="color: #8B92B0; font-size: 0.7rem;">MAX DRAWDOWN</div>
                    <div style="margin-top: 0.5rem; color: #B8C0DC; font-size: 0.85rem;">
                        Avg: <span style="color: {'#FF3B6B' if avg < 0 else '#00F5A0'};">{avg:+.1f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed table
        st.markdown("### Detailed Results")
        pivot = results_df.pivot(index="Event Full", columns="Horizon", values="Return (%)")
        pivot = pivot[["1M", "3M", "6M", "1Y", "2Y"]]
        
        def color_returns(val):
            if pd.isna(val):
                return ""
            color = "#00F5A0" if val > 0 else "#FF3B6B"
            return f"color: {color}; font-weight: 600; font-family: JetBrains Mono;"
        
        st.dataframe(
            pivot.style.applymap(color_returns).format("{:+.2f}%"),
            use_container_width=True
        )
        
        # Risk Analysis
        st.markdown("### Risk Analysis")
        
        worst_scenario = results_df.loc[results_df["Return (%)"].idxmin()]
        best_scenario = results_df.loc[results_df["Return (%)"].idxmax()]
        avg_return = results_df["Return (%)"].mean()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Worst Case Drawdown", f"{worst_scenario['Return (%)']:+.2f}%",
                    f"{worst_scenario['Event Full']} @ {worst_scenario['Horizon']}")
        col2.metric("Best Case Outcome", f"{best_scenario['Return (%)']:+.2f}%",
                    f"{best_scenario['Event Full']} @ {best_scenario['Horizon']}")
        col3.metric("Average Return", f"{avg_return:+.2f}%")
        
        # PDF Export
        st.divider()
        st.markdown("### Export Report")
        
        try:
            pdf_buffer = generate_portfolio_report(
                portfolio={ASSET_LABELS[k]: v for k, v in portfolio.items() if v > 0},
                scenario_name=", ".join(selected_events[:2]) + ("..." if len(selected_events) > 2 else ""),
                results_df=results_df,
                total_impact=avg_return
            )
            
            st.download_button(
                label="⬇Download PDF Report",
                data=pdf_buffer,
                file_name=f"macrolens_stress_test_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"PDF generation requires reportlab: pip install reportlab")