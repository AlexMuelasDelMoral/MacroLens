import streamlit as st
import pandas as pd
from src.styles import apply_custom_theme, render_page_header
from src.navbar import render_navbar
from src.data_loader import (
    get_asset_classes, ASSET_LABELS, ASSET_CATEGORIES, get_categories
)
from src.similarity_engine import find_similar_events, aggregate_impact_prediction
from src.visualizations import (
    plot_similarity_scores, plot_prediction_with_uncertainty, plot_macro_gauge
)
from src.theory_engine import get_relevant_theories
from src.portfolio_state import (
    has_portfolio, get_active_positions, portfolio_summary_string,
    portfolio_as_fractions,
)

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
render_navbar()

render_page_header(
    label="PREDICTIVE ANALYSIS",
    title="Scenario Builder",
    subtitle="Input macro conditions and discover similar historical precedents",
)
st.divider()

if has_portfolio():
    st.info(f"Active portfolio: {portfolio_summary_string()}")

# ============ MACRO INPUT PANEL ============
st.markdown("## Macro Conditions")

if FRED_AVAILABLE:
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("Load Live Data", width='stretch'):
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
        width='stretch'
    )
with cols[1]:
    st.plotly_chart(
        plot_macro_gauge(fed_rate, "Fed Rate", 0, 20, 2, 8),
        width='stretch'
    )
with cols[2]:
    st.plotly_chart(
        plot_macro_gauge(unemployment, "Unemployment", 0, 15, 4, 7),
        width='stretch'
    )
with cols[3]:
    st.plotly_chart(
        plot_macro_gauge(gdp_growth, "GDP Growth", -5, 8, 0, 3),
        width='stretch'
    )

st.divider()

# ============ RUN ANALYSIS ============
user_conditions = {
    "inflation": inflation,
    "fed_funds_rate": fed_rate,
    "unemployment": unemployment,
    "gdp_growth": gdp_growth,
}

if st.button("Analyze Scenario", width='stretch', type="primary"):
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
    st.plotly_chart(plot_similarity_scores(similar_events), width='stretch')

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

    tab1, tab2, tab3, tab4 = st.tabs(["Prediction", "Model Comparison", "Theory", "Monte Carlo"])

    with tab1:
        # BUG FIX: Pass similar_events (the variable) not find_similar_events (the function)
        predictions = aggregate_impact_prediction(similar_events, selected_asset)

        if predictions and any(predictions.get(h) for h in predictions):
            fig = plot_prediction_with_uncertainty(predictions, selected_asset)
            st.plotly_chart(fig, width='stretch')

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
                        std = pred.get("std", 0)
                        n = pred.get("n_samples", 0)
                        val_color = "#00F5A0" if val > 0 else "#FF3B6B"
                        if n >= 8:
                            badge_label = "High confidence"
                            badge_color = "#00F5A0"
                        elif n >= 4:
                            badge_label = "Med confidence"
                            badge_color = "#FFB547"
                        else:
                            badge_label = "Low confidence"
                            badge_color = "#FF3B6B"
                        st.markdown(f"""
                        <div class="glass-card" style="text-align: center;">
                            <div style="color: #8B92B0; font-size: 0.7rem; letter-spacing: 0.1em;">{label}</div>
                            <div style="color: {val_color}; font-family: JetBrains Mono; font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">
                                {val:+.1f}%
                            </div>
                            <div style="color: #5A6182; font-size: 0.7rem;">
                                Range: {pred['min']:+.1f} to {pred['max']:+.1f}%
                            </div>
                            <div style="color: #5A6182; font-size: 0.7rem;">
                                Std dev: {std:+.1f}%
                            </div>
                            <div style="color: {badge_color}; font-size: 0.65rem; margin-top: 0.3rem; font-family: JetBrains Mono;">
                                {badge_label} (n={n})
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
        st.markdown("### Similarity model vs machine learning")
        st.caption("Compare two prediction methodologies and inspect what drives the ML result")

        if not ML_AVAILABLE:
            st.info("ML engine not available.")
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
                    name="Similarity model",
                    x=comp_df["Horizon"],
                    y=comp_df["Similarity Model"],
                    marker_color="#00D4FF",
                ))
                fig.add_trace(go.Bar(
                    name="ML model",
                    x=comp_df["Horizon"],
                    y=comp_df["ML Model"],
                    marker_color="#7C3AED",
                ))

                layout = get_plotly_layout(
                    title="<b>Model comparison</b>",
                    barmode="group",
                    height=400,
                    yaxis_title="Predicted return (%)",
                )
                fig.update_layout(layout)
                st.plotly_chart(fig, width='stretch')
                st.info(
                    "When models agree, confidence is higher. "
                    "Divergence suggests unique scenario characteristics."
                )

                st.divider()
                st.markdown("### Why the ML model made this prediction")
                st.caption(
                    "SHAP values show how each macro variable pushed the prediction "
                    "above or below the baseline average return. "
                    "Positive values push the prediction higher, negative values push it lower."
                )

                shap_horizon = st.select_slider(
                    "Horizon for SHAP analysis",
                    options=["1m", "3m", "6m", "1y", "2y"],
                    value="3m",
                    key="shap_horizon_slider",
                )

                try:
                    from src.ml_engine import get_shap_explanation
                    shap_result = get_shap_explanation(
                        user_conditions=user_conditions,
                        asset_class=selected_asset,
                        horizon=shap_horizon,
                        severity=severity,
                        duration=duration,
                    )

                    if shap_result is None:
                        st.warning(
                            "Insufficient training data for SHAP analysis "
                            "on this asset and horizon."
                        )
                    else:
                        base = shap_result["base_value"]
                        prediction = shap_result["prediction"]
                        names = shap_result["feature_names"]
                        values = shap_result["shap_values"]
                        n = shap_result["n_training_samples"]

                        col_pred, col_base, col_n = st.columns(3)
                        col_pred.metric(
                            "ML prediction",
                            f"{prediction:+.2f}%",
                        )
                        col_base.metric(
                            "Baseline average",
                            f"{base:+.2f}%",
                        )
                        col_n.metric(
                            "Training samples",
                            str(n),
                        )

                        sorted_pairs = sorted(
                            zip(names, values),
                            key=lambda x: abs(x[1]),
                            reverse=True,
                        )
                        sorted_names = [p[0] for p in sorted_pairs]
                        sorted_values = [p[1] for p in sorted_pairs]
                        bar_colors = [
                            "#00F5A0" if v >= 0 else "#FF3B6B"
                            for v in sorted_values
                        ]

                        fig_shap = go.Figure(go.Bar(
                            x=sorted_values,
                            y=sorted_names,
                            orientation="h",
                            marker=dict(
                                color=bar_colors,
                                line=dict(
                                    color="rgba(255,255,255,0.1)",
                                    width=1,
                                ),
                            ),
                            text=[f"{v:+.3f}" for v in sorted_values],
                            textposition="outside",
                            textfont=dict(
                                color="#E4E8F1",
                                size=12,
                                family="JetBrains Mono",
                            ),
                        ))

                        fig_shap.add_vline(
                            x=0,
                            line_dash="dash",
                            line_color="rgba(139, 146, 176, 0.5)",
                            line_width=1,
                        )

                        layout_shap = get_plotly_layout(
                            title=(
                                f"<b>SHAP feature contributions</b>"
                                f"<br><span style='font-size:11px;color:#8B92B0'>"
                                f"Baseline: {base:+.2f}% | "
                                f"Prediction: {prediction:+.2f}% | "
                                f"Horizon: {shap_horizon.upper()}"
                                f"</span>"
                            ),
                            xaxis_title="SHAP value (impact on predicted return %)",
                            height=380,
                            showlegend=False,
                            margin=dict(l=20, r=60, t=100, b=40),
                        )
                        fig_shap.update_layout(layout_shap)
                        st.plotly_chart(fig_shap, width='stretch')

                        st.markdown("#### Reading this chart")
                        st.markdown(
                            "Each bar shows how much that variable moved the "
                            "prediction away from the baseline average return. "
                            "The largest bars are the dominant drivers of this "
                            "specific prediction. Variables close to zero had "
                            "little influence given your current macro inputs."
                        )

                        with st.expander("Raw SHAP values"):
                            shap_table = [
                                {
                                    "Feature": name,
                                    "Input value": round({
                                        "Inflation": user_conditions.get("inflation", 3.0),
                                        "Fed Rate": user_conditions.get("fed_funds_rate", 5.0),
                                        "Unemployment": user_conditions.get("unemployment", 4.0),
                                        "GDP Growth": user_conditions.get("gdp_growth", 2.0),
                                        "Severity": severity,
                                        "Duration": duration,
                                    }.get(name, 0), 2),
                                    "SHAP contribution": f"{val:+.4f}",
                                    "Direction": "Positive" if val >= 0 else "Negative",
                                }
                                for name, val in zip(names, values)
                            ]
                            st.dataframe(
                                shap_table,
                                width='stretch',
                                hide_index=True,
                            )

                except Exception as shap_err:
                    st.warning(f"SHAP analysis unavailable: {shap_err}")

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

    with tab4:
        st.markdown("### Monte Carlo simulation")
        st.caption(
            "Samples 10,000 return paths from the distribution of historical analogs "
            "to produce a full return distribution rather than a point estimate. "
            "Bootstrap resampling preserves the actual shape of historical returns "
            "including skew and fat tails."
        )

        mc_horizon = st.select_slider(
            "Simulation horizon",
            options=["1m", "3m", "6m", "1y", "2y"],
            value="1y",
            key="mc_horizon_slider",
        )

        mc_sims = st.select_slider(
            "Number of simulations",
            options=[1000, 5000, 10000, 50000],
            value=10000,
            key="mc_sims_slider",
        )

        try:
            from src.monte_carlo import run_monte_carlo
            import plotly.graph_objects as go
            from src.styles import get_plotly_layout

            predictions = aggregate_impact_prediction(similar_events, selected_asset)
            h_pred = predictions.get(mc_horizon)

            if h_pred is None:
                st.warning(
                    "No prediction data available for this asset and horizon. "
                    "Try a different asset or horizon."
                )
            else:
                with st.spinner(f"Running {mc_sims:,} simulations..."):
                    mc_result, sim_returns = run_monte_carlo(
                        prediction=h_pred,
                        asset_class=selected_asset,
                        horizon=mc_horizon,
                        n_simulations=mc_sims,
                    )

                if mc_result is None or sim_returns is None:
                    st.warning("Simulation failed. Standard deviation may be zero for this asset.")
                else:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric(
                        "Expected return",
                        f"{mc_result.expected:+.2f}%",
                    )
                    col2.metric(
                        "Prob. positive",
                        f"{mc_result.prob_positive:.1f}%",
                    )
                    col3.metric(
                        "VaR 95",
                        f"{mc_result.var_95:+.2f}%",
                        "5th percentile",
                        delta_color="inverse",
                    )
                    col4.metric(
                        "CVaR 95",
                        f"{mc_result.cvar_95:+.2f}%",
                        "Expected loss beyond VaR",
                        delta_color="inverse",
                    )

                    pass  # sim_returns already returned from run_monte_carlo
                    fig_mc = go.Figure()

                    fig_mc.add_trace(go.Histogram(
                        x=sim_returns,
                        nbinsx=80,
                        name="Simulated returns",
                        marker=dict(
                            color=[
                                "#00F5A0" if v >= 0 else "#FF3B6B"
                                for v in sim_returns
                            ],
                            opacity=0.75,
                            line=dict(color="rgba(255,255,255,0.05)", width=0.5),
                        ),
                        hovertemplate="Return: %{x:.1f}%<br>Count: %{y}<extra></extra>",
                    ))

                    fig_mc.add_vline(
                        x=mc_result.expected,
                        line_dash="solid",
                        line_color="#00D4FF",
                        line_width=2,
                        annotation_text=f"Expected {mc_result.expected:+.1f}%",
                        annotation_font=dict(color="#00D4FF", size=11),
                        annotation_position="top right",
                    )
                    fig_mc.add_vline(
                        x=mc_result.var_95,
                        line_dash="dash",
                        line_color="#FFB547",
                        line_width=2,
                        annotation_text=f"VaR 95 {mc_result.var_95:+.1f}%",
                        annotation_font=dict(color="#FFB547", size=11),
                        annotation_position="top left",
                    )
                    fig_mc.add_vline(
                        x=mc_result.var_99,
                        line_dash="dash",
                        line_color="#FF3B6B",
                        line_width=2,
                        annotation_text=f"VaR 99 {mc_result.var_99:+.1f}%",
                        annotation_font=dict(color="#FF3B6B", size=11),
                        annotation_position="top left",
                    )
                    fig_mc.add_vline(
                        x=0,
                        line_dash="dot",
                        line_color="rgba(139,146,176,0.5)",
                        line_width=1,
                    )

                    asset_label = ASSET_LABELS.get(selected_asset, selected_asset)
                    layout_mc = get_plotly_layout(
                        title=dict(
                            text=(
                                f"<b>Return distribution: {asset_label} — "
                                f"{mc_horizon.upper()} horizon</b>"
                                f"<br><span style='font-size:11px;color:#8B92B0'>"
                                f"{mc_sims:,} simulations from {mc_result.n_historical_analogs} "
                                f"historical analogs. Green = positive return, red = negative.</span>"
                            ),
                            font=dict(size=15, color="#E4E8F1"),
                        ),
                        xaxis_title="Simulated return (%)",
                        yaxis_title="Frequency",
                        height=440,
                        showlegend=True,
                        barmode="overlay",
                        margin=dict(l=40, r=40, t=110, b=40),
                        bargap=0.02,
                    )
                    fig_mc.update_layout(layout_mc)
                    st.plotly_chart(fig_mc, width='stretch')

                    st.markdown("### Percentile breakdown")
                    perc_cols = st.columns(5)
                    percentiles = [
                        ("10th", mc_result.percentile_10),
                        ("25th", mc_result.percentile_25),
                        ("50th", mc_result.percentile_50),
                        ("75th", mc_result.percentile_75),
                        ("90th", mc_result.percentile_90),
                    ]
                    for i, (label, value) in enumerate(percentiles):
                        with perc_cols[i]:
                            color = "#00F5A0" if value >= 0 else "#FF3B6B"
                            st.markdown(f"""
                            <div style="background: rgba(21,26,58,0.6);
                                        border: 0.5px solid rgba(42,49,88,0.5);
                                        border-radius: 8px; padding: 0.75rem;
                                        text-align: center;">
                                <div style="color: #8B92B0; font-size: 0.7rem;
                                            letter-spacing: 0.08em; margin-bottom: 0.3rem;">
                                    {label} PERCENTILE
                                </div>
                                <div style="color: {color}; font-family: JetBrains Mono;
                                            font-size: 1.2rem; font-weight: 700;">
                                    {value:+.1f}%
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown("### Tail risk")
                    risk_cols = st.columns(3)
                    risk_cols[0].metric(
                        "Prob. loss > 10%",
                        f"{mc_result.prob_loss_10pct:.1f}%",
                        delta_color="inverse",
                    )
                    risk_cols[1].metric(
                        "Prob. loss > 20%",
                        f"{mc_result.prob_loss_20pct:.1f}%",
                        delta_color="inverse",
                    )
                    risk_cols[2].metric(
                        "CVaR 99",
                        f"{mc_result.cvar_99:+.2f}%",
                        "Expected loss in worst 1%",
                        delta_color="inverse",
                    )

                    st.caption(
                        "VaR (Value at Risk) is the return threshold at the given confidence level. "
                        "CVaR (Conditional VaR) is the average return in the worst scenarios beyond "
                        "that threshold. Both are based on simulated paths, not guaranteed outcomes."
                    )

        except Exception as mc_err:
            st.warning(f"Monte Carlo simulation unavailable: {mc_err}")

# ============ PORTFOLIO IMPACT PANEL ============
    if has_portfolio():
        st.divider()
        st.markdown("## Active Portfolio Impact")
        st.caption(
            "Weighted return estimate for your active portfolio under this scenario, "
            "using the same similarity-weighted methodology as individual asset predictions."
        )

        positions = get_active_positions()
        fractions = portfolio_as_fractions()

        horizon_labels = [
            ("1m", "1 Month"), ("3m", "3 Months"),
            ("6m", "6 Months"), ("1y", "1 Year"), ("2y", "2 Years"),
        ]

        portfolio_predictions: dict[str, dict[str, float | None]] = {
            h: {"weighted": None, "min": None, "max": None}
            for h, _ in horizon_labels
        }

        for asset_id, fraction in fractions.items():
            pred = aggregate_impact_prediction(similar_events, asset_id)
            if not pred:
                continue
            for horizon, _ in horizon_labels:
                h_pred = pred.get(horizon)
                if h_pred is None:
                    continue
                current = portfolio_predictions[horizon]["weighted"] or 0.0
                portfolio_predictions[horizon]["weighted"] = (
                    current + fraction * h_pred["expected"]
                )

        cols = st.columns(5)
        for i, (horizon, label) in enumerate(horizon_labels):
            value = portfolio_predictions[horizon]["weighted"]
            with cols[i]:
                if value is not None:
                    color = "#00F5A0" if value > 0 else "#FF3B6B"
                    st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <div style="color: #8B92B0; font-size: 0.7rem; letter-spacing: 0.1em;">{label}</div>
                        <div style="color: {color}; font-family: JetBrains Mono;
                                    font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">
                            {value:+.1f}%
                        </div>
                        <div style="color: #5A6182; font-size: 0.7rem;">Portfolio weighted</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <div style="color: #8B92B0; font-size: 0.7rem;">{label}</div>
                        <div style="color: #5A6182;">N/A</div>
                    </div>
                    """, unsafe_allow_html=True)

        with st.expander("Holdings used in this estimate"):
            rows = [
                {"Asset": ASSET_LABELS.get(k, k), "Weight": f"{v:.1f}%"}
                for k, v in sorted(positions.items(), key=lambda x: -x[1])
            ]
            st.dataframe(rows, width='stretch', hide_index=True)

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
                    width='stretch',
                )
            except Exception as e:
                st.error(f"PDF generation error: {e}")