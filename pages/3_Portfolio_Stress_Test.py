import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.impact_matrix import build_impact_matrix, compute_portfolio_returns
from src.constants import HORIZONS, HORIZON_LABELS, PRESET_PORTFOLIOS as PRESETS
from src.styles import apply_custom_theme, get_plotly_layout, render_page_header
from src.navbar import render_navbar
from src.data_loader import load_events, load_impacts, ASSET_LABELS, ASSET_CATEGORIES
from src.visualizations import plot_portfolio_performance
from src.report_generator import generate_portfolio_report
from src.portfolio_parser import parse_portfolio, PortfolioParseError
from src.portfolio_state import (
    sync_from_stress_test_widgets,
    has_portfolio,
    encode_portfolio_for_url,
    decode_portfolio_from_url,
    portfolio_to_csv,
    portfolio_to_json,
)

def _load_state_from_url() -> None:
    params = st.query_params
    raw_portfolio = params.get("port", "")
    if raw_portfolio and "url_portfolio_loaded" not in st.session_state:
        weights = decode_portfolio_from_url(raw_portfolio)
        if weights:
            for asset_id in ASSET_LABELS:
                st.session_state[f"port_{asset_id}"] = weights.get(asset_id, 0.0)
            st.session_state["url_portfolio_loaded"] = True
    raw_events = params.get("events", "")
    if raw_events and "url_events_loaded" not in st.session_state:
        st.session_state["url_selected_event_ids"] = set(raw_events.split(","))
        st.session_state["url_events_loaded"] = True


_load_state_from_url()

st.set_page_config(page_title="Portfolio Stress Test", layout="wide")
apply_custom_theme()
render_navbar()

render_page_header(
    label="STRESS TESTING",
    title="Portfolio Stress Test",
    subtitle="Simulate your portfolio's behavior under 30 historical crisis scenarios across 45 asset classes",
)
if has_portfolio():
    st.info(
        "Your portfolio is active across all pages. "
        "Scenario Builder and Live Dashboard will use it automatically."
    )

st.divider()


@st.cache_data(show_spinner=False)
def _parse_cached(text: str, label_signature: tuple) -> dict:
    labels = dict(label_signature)
    result = parse_portfolio(text, labels)
    return {
        "weights": result.weights,
        "warnings": list(result.warnings),
        "invalid": list(result.invalid_entries),
        "original_sum": result.original_sum,
        "was_normalized": result.was_normalized,
    }


def _apply_to_session_state(weights_fraction: dict) -> None:
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
                if f"port_{asset_id}" not in st.session_state:
                    st.session_state[f"port_{asset_id}"] = float(default_val)
                portfolio[asset_id] = st.number_input(
                    asset_name,
                    min_value=0.0, max_value=100.0,
                    step=1.0,
                    key=f"port_{asset_id}"
                )

total = sum(portfolio.values())
sync_from_stress_test_widgets()

st.markdown("### Allocation Summary")
col1, col2 = st.columns([3, 1])

with col1:
    st.progress(min(total / 100, 1.0), text=f"Total Allocated: {total:.1f}% / 100%")
with col2:
    if abs(total - 100) > 0.1:
        st.error(f"Off by {100 - total:+.1f}%")
    else:
        st.success("100% Allocated")

if total > 0:
    active_weights = {k: v for k, v in portfolio.items() if v > 0}
    with st.expander("Export portfolio", expanded=False):
        st.caption(
            "Download your portfolio in any format the bulk paste box accepts. "
            "Use these to save your work or share with colleagues."
        )
        col_csv, col_json = st.columns(2)
        with col_csv:
            st.download_button(
                label="Download CSV",
                data=portfolio_to_csv(active_weights),
                file_name=f"macrolens_portfolio_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width='stretch',
            )
        with col_json:
            st.download_button(
                label="Download JSON",
                data=portfolio_to_json(active_weights),
                file_name=f"macrolens_portfolio_{pd.Timestamp.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                width='stretch',
            )
        st.markdown("**Preview (CSV format)**")
        st.code(portfolio_to_csv(active_weights), language="text")

if total > 0:
    active_portfolio = {k: v for k, v in portfolio.items() if v > 0}
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = go.Figure(data=[go.Pie(
            labels=[ASSET_LABELS[k] for k in active_portfolio.keys()],
            values=list(active_portfolio.values()),
            hole=0.6,
            marker=dict(
                colors=[
                    '#00D4FF', '#7C3AED', '#00F5A0', '#FFB547', '#FF3B6B',
                    '#0066FF', '#FF6B00', '#A78BFA', '#06B6D4', '#F472B6',
                    '#FFD700', '#FF69B4', '#00FA9A', '#1E90FF', '#FFA07A',
                ],
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
        st.plotly_chart(fig, width='stretch')
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

filtered_events = [
    e for e in events
    if e['id'] in impacts and e['severity'] >= severity_min
]
if category_filter:
    filtered_events = [e for e in filtered_events if e['category'] in category_filter]

event_options = {
    f"{e['name']} ({e['year']}) — Severity {e['severity']}/10": e['id']
    for e in sorted(filtered_events, key=lambda x: -x['severity'])
}

url_event_ids = st.session_state.get("url_selected_event_ids", set())
default_events = (
    [k for k, v in event_options.items() if v in url_event_ids]
    if url_event_ids
    else list(event_options.keys())[:5]
) if event_options else []

selected_events = st.multiselect(
    f"Choose scenarios ({len(event_options)} available)",
    options=list(event_options.keys()),
    default=default_events,
    key="scenario_multiselect",
)

if selected_events:
    selected_ids = [event_options[d] for d in selected_events]
    st.query_params["events"] = ",".join(selected_ids)

compare_mode = st.checkbox(
    "Compare two scenarios side by side",
    value=False,
    help="Enable to select a second set of scenarios and compare results in parallel columns.",
)

if compare_mode:
    st.markdown("### Comparison scenario")
    st.caption(
        "Select a second group of scenarios to compare against your primary selection above. "
        "The delta column shows the difference in projected returns."
    )

    filtered_events_b = [
        e for e in events
        if e['id'] in impacts and e['severity'] >= severity_min
    ]
    if category_filter:
        filtered_events_b = [
            e for e in filtered_events_b
            if e['category'] in category_filter
        ]

    event_options_b = {
        f"{e['name']} ({e['year']}) — Severity {e['severity']}/10": e['id']
        for e in sorted(filtered_events_b, key=lambda x: -x['severity'])
    }

    selected_events_b = st.multiselect(
        f"Comparison scenarios ({len(event_options_b)} available)",
        options=list(event_options_b.keys()),
        default=list(event_options_b.keys())[5:10] if len(event_options_b) > 5 else [],
        key="scenario_multiselect_b",
    )
else:
    selected_events_b = []
    event_options_b = {}

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("")
with col2:
    run_test = st.button("Run Stress Test", width='stretch', type="primary")

if total > 0:
    active = {k: v for k, v in portfolio.items() if v > 0}
    st.query_params["port"] = encode_portfolio_for_url(active)

if total > 0 and selected_events:
    st.caption(
        "Share this stress test: copy the browser URL. "
        "Anyone with the link opens the same portfolio and scenario selection."
    )

if run_test:
    if abs(total - 100) > 0.1:
        st.error("Portfolio must sum to 100% before running stress test")
    elif not selected_events:
        st.error("Please select at least one scenario")
    else:
        st.divider()
        st.markdown("## Stress Test Results")

        matrix = build_impact_matrix()

        selected_event_ids = [event_options[d] for d in selected_events]
        display_name_for = {v: k for k, v in event_options.items()}

        portfolio_fractions = {
            asset_id: weight / 100.0
            for asset_id, weight in portfolio.items()
            if weight > 0
        }

        vectorized_results = compute_portfolio_returns(
            matrix, portfolio_fractions, selected_event_ids
        )

        results = []
        for event_id, horizon_returns in vectorized_results.items():
            display_name = display_name_for.get(event_id, event_id)
            for horizon in HORIZONS:
                value = horizon_returns.get(horizon)
                results.append({
                    "Event Full": display_name,
                    "Horizon": HORIZON_LABELS[horizon],
                    "Return (%)": value if value is not None else 0.0,
                })
        results_df = pd.DataFrame(results)

        if compare_mode and selected_events_b:
            selected_event_ids_b = [event_options_b[d] for d in selected_events_b]
            display_name_for_b = {v: k for k, v in event_options_b.items()}

            vectorized_results_b = compute_portfolio_returns(
                matrix, portfolio_fractions, selected_event_ids_b
            )

            results_b = []
            for event_id, horizon_returns in vectorized_results_b.items():
                display_name = display_name_for_b.get(event_id, event_id)
                for horizon in HORIZONS:
                    value = horizon_returns.get(horizon)
                    results_b.append({
                        "Event Full": display_name,
                        "Horizon": HORIZON_LABELS[horizon],
                        "Return (%)": value if value is not None else 0.0,
                    })
            results_df_b = pd.DataFrame(results_b)


            st.markdown("#### Primary scenarios")
            fig_a = go.Figure()
            horizons_order = ["1M", "3M", "6M", "1Y", "2Y"]
            colors = ['#00D4FF', '#7C3AED', '#00F5A0', '#FFB547', '#FF3B6B',
                      '#0066FF', '#FF6B00', '#A78BFA', '#06B6D4', '#F472B6']

            avg_a_by_horizon = results_df.groupby("Horizon")["Return (%)"].mean().reindex(horizons_order)
            fig_a.add_trace(go.Bar(
                x=horizons_order,
                y=avg_a_by_horizon.values,
                name="Average return",
                marker=dict(
                    color=["#00F5A0" if v >= 0 else "#FF3B6B" for v in avg_a_by_horizon.values],
                    opacity=0.9,
                    line=dict(color="rgba(255,255,255,0.15)", width=1),
                ),
                text=[f"{v:+.1f}%" for v in avg_a_by_horizon.values],
                textposition="outside",
                textfont=dict(color="#E4E8F1", size=13, family="JetBrains Mono"),
            ))

            for i, event_name in enumerate(selected_events):
                event_data = results_df[results_df["Event Full"] == event_name]
                if len(event_data) == 0:
                    continue
                event_data = event_data.set_index("Horizon").reindex(horizons_order)
                fig_a.add_trace(go.Scatter(
                    x=horizons_order,
                    y=event_data["Return (%)"].values,
                    mode="lines+markers",
                    name=event_name.split(" (")[0],
                    marker=dict(
                        size=10,
                        color=colors[i % len(colors)],
                        opacity=1.0,
                        line=dict(color="rgba(255,255,255,0.5)", width=2),
                    ),
                    line=dict(width=2, color=colors[i % len(colors)]),
                    hovertemplate=f"<b>{event_name.split(' (')[0]}</b><br>%{{x}}: %{{y:+.2f}}%<extra></extra>",
                ))

            fig_a.add_hline(y=0, line_dash="dash",
                            line_color="rgba(139,146,176,0.4)", line_width=1)
            layout_a = get_plotly_layout(
                title=dict(
                    text="<b>Primary scenarios — average return per horizon</b>"
                         "<br><span style='font-size:11px;color:#8B92B0'>"
                         "Bars show average across all selected events. "
                         "Dots show individual event returns.</span>",
                    font=dict(size=15, color="#E4E8F1"),
                ),
                xaxis_title="Time horizon",
                yaxis_title="Portfolio return (%)",
                height=420,
                barmode="overlay",
                hovermode="x unified",
                margin=dict(l=40, r=40, t=100, b=40),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.35,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11),
                ),
            )
            fig_a.update_layout(layout_a)
            st.plotly_chart(fig_a, width='stretch')

            avg_a = results_df["Return (%)"].mean()
            worst_a = results_df.loc[results_df["Return (%)"].idxmin()]
            best_a = results_df.loc[results_df["Return (%)"].idxmax()]

            st.divider()
            st.markdown("#### Comparison scenarios")

            avg_b_by_horizon = results_df_b.groupby("Horizon")["Return (%)"].mean().reindex(horizons_order)
            fig_b = go.Figure()
            fig_b.add_trace(go.Bar(
                x=horizons_order,
                y=avg_b_by_horizon.values,
                name="Average return",
                marker=dict(
                    color=["#00F5A0" if v >= 0 else "#FF3B6B" for v in avg_b_by_horizon.values],
                    opacity=0.9,
                    line=dict(color="rgba(255,255,255,0.15)", width=1),
                ),
                text=[f"{v:+.1f}%" for v in avg_b_by_horizon.values],
                textposition="outside",
                textfont=dict(color="#E4E8F1", size=13, family="JetBrains Mono"),
            ))

            for i, event_name in enumerate(selected_events_b):
                event_data = results_df_b[results_df_b["Event Full"] == event_name]
                if len(event_data) == 0:
                    continue
                event_data = event_data.set_index("Horizon").reindex(horizons_order)
                fig_b.add_trace(go.Scatter(
                    x=horizons_order,
                    y=event_data["Return (%)"].values,
                    mode="lines+markers",
                    name=event_name.split(" (")[0],
                    marker=dict(
                        size=10,
                        color=colors[i % len(colors)],
                        opacity=1.0,
                        line=dict(color="rgba(255,255,255,0.5)", width=2),
                    ),
                    line=dict(width=2, color=colors[i % len(colors)]),
                    hovertemplate=f"<b>{event_name.split(' (')[0]}</b><br>%{{x}}: %{{y:+.2f}}%<extra></extra>",
                ))

            fig_b.add_hline(y=0, line_dash="dash",
                            line_color="rgba(139,146,176,0.4)", line_width=1)
            layout_b = get_plotly_layout(
                title=dict(
                    text="<b>Comparison scenarios — average return per horizon</b>"
                         "<br><span style='font-size:11px;color:#8B92B0'>"
                         "Bars show average across all selected events. "
                         "Dots show individual event returns.</span>",
                    font=dict(size=15, color="#E4E8F1"),
                ),
                xaxis_title="Time horizon",
                yaxis_title="Portfolio return (%)",
                height=420,
                barmode="overlay",
                hovermode="x unified",
                margin=dict(l=40, r=40, t=100, b=40),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.35,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11),
                ),
            )
            fig_b.update_layout(layout_b)
            st.plotly_chart(fig_b, width='stretch')

            avg_b = results_df_b["Return (%)"].mean()
            worst_b = results_df_b.loc[results_df_b["Return (%)"].idxmin()]
            best_b = results_df_b.loc[results_df_b["Return (%)"].idxmax()]

            st.divider()
            st.markdown("#### Delta — comparison minus primary")
            st.caption(
                "Positive delta means the comparison scenario group produced "
                "a better outcome for this portfolio at that horizon."
            )

            delta_cols = st.columns(5)
            for i, horizon_label in enumerate(horizons_order):
                a_val = avg_a_by_horizon.get(horizon_label, 0.0)
                b_val = avg_b_by_horizon.get(horizon_label, 0.0)
                delta_val = b_val - a_val
                with delta_cols[i]:
                    st.metric(
                        label=horizon_label,
                        value=f"{delta_val:+.2f}%",
                        delta=f"A: {a_val:+.1f}% B: {b_val:+.1f}%",
                        delta_color="normal" if delta_val >= 0 else "inverse",
                    )

            summary_cols = st.columns(3)
            delta_avg = avg_b - avg_a
            delta_worst = worst_b["Return (%)"] - worst_a["Return (%)"]
            delta_best = best_b["Return (%)"] - best_a["Return (%)"]
            summary_cols[0].metric("Avg return delta",
                f"{delta_avg:+.2f}%", "Overall average",
                delta_color="normal" if delta_avg >= 0 else "inverse")
            summary_cols[1].metric("Worst case delta",
                f"{delta_worst:+.2f}%",
                delta_color="normal" if delta_worst >= 0 else "inverse")
            summary_cols[2].metric("Best case delta",
                f"{delta_best:+.2f}%",
                delta_color="normal" if delta_best >= 0 else "inverse")

            tab_a, tab_b = st.tabs(["Primary scenarios", "Comparison scenarios"])

            def color_returns(val):
                if pd.isna(val):
                    return ""
                color = "#00F5A0" if val > 0 else "#FF3B6B"
                return f"color: {color}; font-weight: 600; font-family: JetBrains Mono;"

            with tab_a:
                pivot_a_full = results_df.pivot(
                    index="Event Full", columns="Horizon", values="Return (%)"
                ).reindex(columns=["1M", "3M", "6M", "1Y", "2Y"])
                st.dataframe(
                    pivot_a_full.style.map(color_returns).format("{:+.2f}%"),
                    width='stretch', height=400,
                )
            with tab_b:
                pivot_b_full = results_df_b.pivot(
                    index="Event Full", columns="Horizon", values="Return (%)"
                ).reindex(columns=["1M", "3M", "6M", "1Y", "2Y"])
                st.dataframe(
                    pivot_b_full.style.map(color_returns).format("{:+.2f}%"),
                    width='stretch', height=400,
                )

        else:
            fig = plot_portfolio_performance(results_df, selected_events)
            st.plotly_chart(fig, width='stretch')

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
            pivot = results_df.pivot(
                index="Event Full", columns="Horizon", values="Return (%)"
            )
            pivot = pivot[["1M", "3M", "6M", "1Y", "2Y"]]

            def color_returns(val):
                if pd.isna(val):
                    return ""
                color = "#00F5A0" if val > 0 else "#FF3B6B"
                return f"color: {color}; font-weight: 600; font-family: JetBrains Mono;"

            st.dataframe(
                pivot.style.map(color_returns).format("{:+.2f}%"),
                width='stretch', height=400,
            )

            st.divider()
            try:
                pdf_buffer = generate_portfolio_report(
                    portfolio={ASSET_LABELS[k]: v for k, v in portfolio.items() if v > 0},
                    scenario_name=f"{len(selected_events)} scenarios tested",
                    results_df=results_df,
                    total_impact=avg,
                )
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"macrolens_stress_test_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    width='stretch',
                )
            except Exception as e:
                st.warning(f"PDF generation unavailable: {e}")
