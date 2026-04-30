import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.styles import apply_custom_theme, get_plotly_layout
from src.data_loader import load_events, load_impacts, ASSET_LABELS, ASSET_CATEGORIES
from src.visualizations import plot_portfolio_performance
from src.report_generator import generate_portfolio_report
from src.portfolio_parser import parse_portfolio, PortfolioParseError

st.set_page_config(page_title="Portfolio Stress Test", layout="wide")
apply_custom_theme()

st.markdown('<div class="section-label">STRESS TESTING</div>', unsafe_allow_html=True)
st.markdown("# Portfolio Stress Test")
st.caption("Simulate your portfolio's behavior under 30 historical crisis scenarios across 45 asset classes")

st.divider()

from src.constants import PRESET_PORTFOLIOS as PRESETS

@st.cache_data(show_spinner=False)
def _parse_cached(text: str, label_signature: tuple[tuple[str, str], ...]) -> dict:
    """Cache parses keyed on input text plus the asset universe.

    The label_signature tuple makes the cache key hashable and invalidates
    automatically if ASSET_LABELS changes between runs.
    """
    labels = dict(label_signature)
    result = parse_portfolio(text, labels)
    return {
        "weights": result.weights,
        "warnings": list(result.warnings),
        "invalid": list(result.invalid_entries),
        "original_sum": result.original_sum,
        "was_normalized": result.was_normalized,
    }


def _apply_to_session_state(weights_fraction: dict[str, float]) -> None:
    """Push parsed weights into the port_* session state keys so the
    category tabs render with the new allocation on rerun."""
    for asset_id in ASSET_LABELS:
        st.session_state[f"port_{asset_id}"] = 0.0
    for asset_id, fraction in weights_fraction.items():
        st.session_state[f"port_{asset_id}"] = round(fraction * 100.0, 2)


st.markdown("## Build Your Portfolio")

col1, col2 = st.columns([2, 1])
with col1:
    preset = st.selectbox("Preset Portfolio", list(PRESETS.keys()))
with col2:
    if st.button("Reset Portfolio"):
        for key in list(st.session_state.keys()):
            if key.startswith("port_"):
                del st.session_state[key]
        st.rerun()

with st.expander("Bulk paste portfolio", expanded=False):
    st.caption(
        "Paste an entire portfolio in any of these formats. Mix freely, "
        "one entry per line. Weights auto-scale to 100 percent."
    )
    st.markdown(
        "- Space:  `sp500 35`  \n"
        "- Comma:  `sp500,35`  \n"
        "- Colon with percent:  `sp500: 35%`  \n"
        "- Tab-separated (Excel paste):  `sp500\\t35`  \n"
        "- JSON:  `{\"sp500\": 35, \"bitcoin\": 10}`  \n"
        "Use either the asset ID (`sp500`, `us_10y_treasury`) or the "
        "display name (`S&P 500`, `US 10Y Treasury`)."
    )
    pasted = st.text_area(
        "Portfolio definition",
        height=180,
        placeholder="sp500 35\nnasdaq 20\nbitcoin 10\ngold 25\nus_10y_treasury 10",
        key="bulk_paste_text",
        label_visibility="collapsed",
    )
    apply_clicked = st.button("Apply pasted portfolio", type="primary", key="bulk_apply")

    if apply_clicked:
        if not pasted.strip():
            st.error("Paste a portfolio above before applying.")
        else:
            try:
                label_signature = tuple(sorted(ASSET_LABELS.items()))
                result = _parse_cached(pasted, label_signature)
            except PortfolioParseError as exc:
                st.error(f"Could not parse: {exc}")
            else:
                for message in result["warnings"]:
                    st.warning(message)
                _apply_to_session_state(result["weights"])
                st.success(
                    f"Loaded {len(result['weights'])} positions. "
                    "Refine values in the category tabs below."
                )
                st.rerun()

st.caption("Expand categories below to allocate across 45 asset classes")

portfolio = {}

category_names = list(ASSET_CATEGORIES.keys())
tabs = st.tabs([f"{cat}" for cat in category_names])

for i, (tab, category) in enumerate(zip(tabs, category_names)):
    with tab:
        assets = ASSET_CATEGORIES[category]
        cols = st.columns(3)
        for j, (asset_id, asset_name) in enumerate(assets.items()):
            default_val = PRESETS.get(preset, {}).get(asset_id, 0)
            with cols[j % 3]:
                portfolio[asset_id] = st.number_input(
                    asset_name,
                    min_value=0.0, max_value=100.0,
                    value=float(default_val),
                    step=1.0,
                    key=f"port_{asset_id}"
                )

total = sum(portfolio.values())

st.markdown("### Allocation Summary")
col1, col2 = st.columns([3, 1])

with col1:
    st.progress(min(total / 100, 1.0),
                text=f"Total Allocated: {total:.1f}% / 100%")

with col2:
    if abs(total - 100) > 0.1:
        st.error(f"Off by {100 - total:+.1f}%")
    else:
        st.success("100% Allocated")

if total > 0:
    active_portfolio = {k: v for k, v in portfolio.items() if v > 0}

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = go.Figure(data=[go.Pie(
            labels=[ASSET_LABELS[k] for k in active_portfolio.keys()],
            values=list(active_portfolio.values()),
            hole=0.6,
            marker=dict(
                colors=['#00D4FF', '#7C3AED', '#00F5A0', '#FFB547', '#FF3B6B',
                         '#0066FF', '#FF6B00', '#A78BFA', '#06B6D4', '#F472B6',
                         '#FFD700', '#FF69B4', '#00FA9A', '#1E90FF', '#FFA07A'],
                line=dict(color='#0A0E27', width=2)
            ),
            textfont=dict(color='#E4E8F1', size=10),
            textposition='outside',
            textinfo='label+percent'
        )])

        layout = get_plotly_layout(
            title="<b>Portfolio Allocation</b>",
            height=500,
            showlegend=False
        )
        layout['annotations'] = [dict(
            text=f'<b>{total:.0f}%</b><br><span style="font-size:12px;color:#8B92B0">Allocated</span>',
            x=0.5, y=0.5, font_size=28, showarrow=False,
            font=dict(color='#00D4FF')
        )]
        fig.update_layout(layout)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Holdings")
        sorted_holdings = sorted(active_portfolio.items(), key=lambda x: -x[1])
        for asset_id, weight in sorted_holdings[:10]:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 0.4rem 0; border-bottom: 1px solid rgba(42, 49, 88, 0.3);">
                <span style="color: #B8C0DC; font-size: 0.85rem;">{ASSET_LABELS[asset_id]}</span>
                <span style="color: #00D4FF; font-family: 'JetBrains Mono'; font-weight: 600;">{weight}%</span>
            </div>
            """, unsafe_allow_html=True)
        if len(sorted_holdings) > 10:
            st.caption(f"+ {len(sorted_holdings) - 10} more")

st.divider()

st.markdown("## Select Stress Test Scenarios")

events = load_events()
impacts = load_impacts()

events_by_category = {}
for e in events:
    if e['id'] in impacts:
        events_by_category.setdefault(e['category'], []).append(e)

col1, col2 = st.columns([3, 1])

with col1:
    category_filter = st.multiselect(
        "Filter by category",
        options=sorted(events_by_category.keys()),
        default=[]
    )

with col2:
    severity_min = st.slider("Min severity", 1, 10, 1)

filtered_events = [e for e in events if e['id'] in impacts and e['severity'] >= severity_min]
if category_filter:
    filtered_events = [e for e in filtered_events if e['category'] in category_filter]

event_options = {f"{e['name']} ({e['year']}) — Severity {e['severity']}/10": e['id']
                 for e in sorted(filtered_events, key=lambda x: -x['severity'])}

selected_events = st.multiselect(
    f"Choose scenarios ({len(event_options)} available)",
    options=list(event_options.keys()),
    default=list(event_options.keys())[:5] if event_options else []
)

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("")
with col2:
    run_test = st.button("Run Stress Test", use_container_width=True, type="primary")

if run_test:
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
                total_weight_applied = 0

                for asset, weight in portfolio.items():
                    if weight == 0 or asset not in event_impacts:
                        continue
                    asset_return = event_impacts[asset].get(horizon)
                    if asset_return is None:
                        continue
                    weighted_return += (weight / 100) * asset_return
                    total_weight_applied += weight

                if total_weight_applied > 0 and total_weight_applied < 100:
                    weighted_return = weighted_return * (100 / total_weight_applied)

                results.append({
                    "Event Full": event_display_name,
                    "Horizon": horizon.upper(),
                    "Return (%)": round(weighted_return, 2)
                })

        results_df = pd.DataFrame(results)

        fig = plot_portfolio_performance(results_df, selected_events)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Key Metrics")

        worst = results_df.loc[results_df["Return (%)"].idxmin()]
        best = results_df.loc[results_df["Return (%)"].idxmax()]
        avg = results_df["Return (%)"].mean()
        median = results_df["Return (%)"].median()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Worst Case", f"{worst['Return (%)']:+.2f}%",
                    f"{worst['Event Full'][:30]}...", delta_color="inverse")
        col2.metric("Best Case", f"{best['Return (%)']:+.2f}%",
                    f"{best['Event Full'][:30]}...")
        col3.metric("Average Return", f"{avg:+.2f}%")
        col4.metric("Median Return", f"{median:+.2f}%")

        st.markdown("### Detailed Results Matrix")
        pivot = results_df.pivot(index="Event Full", columns="Horizon", values="Return (%)")
        pivot = pivot[["1M", "3M", "6M", "1Y", "2Y"]]

        def color_returns(val):
            if pd.isna(val):
                return ""
            color = "#00F5A0" if val > 0 else "#FF3B6B"
            return f"color: {color}; font-weight: 600; font-family: JetBrains Mono;"

        st.dataframe(
            pivot.style.map(color_returns).format("{:+.2f}%"),
            use_container_width=True,
            height=400
        )

        st.divider()
        try:
            pdf_buffer = generate_portfolio_report(
                portfolio={ASSET_LABELS[k]: v for k, v in portfolio.items() if v > 0},
                scenario_name=f"{len(selected_events)} scenarios tested",
                results_df=results_df,
                total_impact=avg
            )
            st.download_button(
                label="Download PDF Report",
                data=pdf_buffer,
                file_name=f"macrolens_stress_test_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"PDF generation unavailable: {e}")