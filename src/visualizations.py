import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from src.data_loader import ASSET_LABELS
from src.styles import get_plotly_layout

COLORS = {
    "positive": "#00F5A0",
    "negative": "#FF3B6B",
    "neutral": "#8B92B0",
    "primary": "#00D4FF",
    "secondary": "#7C3AED",
    "warning": "#FFB547",
    "bg_card": "rgba(21, 26, 58, 0.4)"
}

def plot_impact_bar(impact_data, asset_class, event_name):
    """Horizontal bar chart showing impact across time horizons."""
    horizons = ["1m", "3m", "6m", "1y", "2y"]
    horizon_labels = ["1 Month", "3 Months", "6 Months", "1 Year", "2 Years"]
    
    values = [impact_data.get(h) for h in horizons]
    colors = [COLORS["positive"] if v and v > 0 else COLORS["negative"] 
              for v in values]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=horizon_labels,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.1)', width=1)
        ),
        text=[f"{v:+.1f}%" if v is not None else "N/A" for v in values],
        textposition='outside',
        textfont=dict(color='#E4E8F1', size=13, family='JetBrains Mono')
    ))
    
    layout = get_plotly_layout(
        title=dict(
            text=f"<b>{ASSET_LABELS.get(asset_class, asset_class)}</b><br><span style='font-size:12px;color:#8B92B0'>{event_name}</span>",
            font=dict(size=18, color='#E4E8F1')
        ),
        xaxis_title="Return (%)",
        yaxis_title="",
        height=400,
        showlegend=False,
        margin=dict(l=20, r=40, t=80, b=40)
    )
    fig.update_layout(layout)
    fig.add_vline(x=0, line_dash="dash", line_color="rgba(139, 146, 176, 0.5)", line_width=1)
    return fig


def plot_multi_asset_heatmap(impacts, event_id):
    """Heatmap of all asset impacts across time horizons."""
    event_impacts = impacts.get(event_id, {})
    horizons = ["1m", "3m", "6m", "1y", "2y"]
    
    data = []
    assets = []
    for asset, values in event_impacts.items():
        row = [values.get(h) for h in horizons]
        if any(v is not None for v in row):
            data.append(row)
            assets.append(ASSET_LABELS.get(asset, asset))
    
    # Custom colorscale: red -> dark -> cyan/green
    custom_colorscale = [
        [0, '#FF3B6B'],
        [0.25, '#8B1A3C'],
        [0.5, '#131836'],
        [0.75, '#0088AA'],
        [1, '#00F5A0']
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=["1M", "3M", "6M", "1Y", "2Y"],
        y=assets,
        colorscale=custom_colorscale,
        zmid=0,
        text=[[f"{v:+.1f}%" if v is not None else "—" for v in row] for row in data],
        texttemplate="%{text}",
        textfont={"size": 11, "family": "JetBrains Mono", "color": "#E4E8F1"},
        hoverongaps=False,
        colorbar=dict(
            title=dict(text="Return %", font=dict(color="#E4E8F1")),
            tickfont=dict(color="#8B92B0"),
            bgcolor="rgba(19, 24, 54, 0.5)",
            bordercolor="rgba(42, 49, 88, 0.5)",
            borderwidth=1
        )
    ))
    
    layout = get_plotly_layout(
        title=dict(
            text="<b>Asset Class Impact Matrix</b>",
            font=dict(size=18, color='#E4E8F1')
        ),
        xaxis_title="Time Horizon",
        height=550,
        margin=dict(l=140, r=40, t=80, b=40)
    )
    fig.update_layout(layout)
    return fig


def plot_similarity_scores(similar_events):
    """Bar chart of similarity scores for matched events."""
    names = [item["event"]["name"] for item in similar_events]
    scores = [item["similarity"] for item in similar_events]
    years = [item["event"]["year"] for item in similar_events]
    
    # Gradient colors based on similarity
    colors = []
    for s in scores:
        if s >= 75:
            colors.append('#00D4FF')
        elif s >= 50:
            colors.append('#7C3AED')
        else:
            colors.append('#5A6182')
    
    fig = go.Figure(go.Bar(
        x=scores,
        y=[f"{n} ({y})" for n, y in zip(names, years)],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0, 212, 255, 0.3)', width=1)
        ),
        text=[f"<b>{s}%</b>" for s in scores],
        textposition='outside',
        textfont=dict(color='#00D4FF', size=13, family='JetBrains Mono')
    ))
    
    layout = get_plotly_layout(
        title=dict(
            text="<b>Historical Pattern Match Analysis</b>",
            font=dict(size=18, color='#E4E8F1')
        ),
        xaxis=dict(
            title="Similarity Score",
            range=[0, 115],
            ticksuffix="%"
        ),
        height=400,
        margin=dict(l=20, r=60, t=80, b=40)
    )
    fig.update_layout(layout)
    return fig


def plot_prediction_with_uncertainty(predictions, asset_class):
    """Line chart with confidence bands for predictions."""
    horizons = ["1m", "3m", "6m", "1y", "2y"]
    horizon_labels = ["1M", "3M", "6M", "1Y", "2Y"]
    
    expected = [predictions[h]["expected"] if predictions[h] else None for h in horizons]
    mins = [predictions[h]["min"] if predictions[h] else None for h in horizons]
    maxs = [predictions[h]["max"] if predictions[h] else None for h in horizons]
    
    fig = go.Figure()
    
    # Uncertainty band with glow
    fig.add_trace(go.Scatter(
        x=horizon_labels + horizon_labels[::-1],
        y=maxs + mins[::-1],
        fill='toself',
        fillcolor='rgba(0, 212, 255, 0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Historical Range',
        showlegend=True,
        hoverinfo='skip'
    ))
    
    # Min line (dashed)
    fig.add_trace(go.Scatter(
        x=horizon_labels,
        y=mins,
        mode='lines',
        name='Worst Case',
        line=dict(color='#FF3B6B', width=1, dash='dot'),
        hovertemplate='%{y:.1f}%<extra></extra>'
    ))
    
    # Max line (dashed)
    fig.add_trace(go.Scatter(
        x=horizon_labels,
        y=maxs,
        mode='lines',
        name='Best Case',
        line=dict(color='#00F5A0', width=1, dash='dot'),
        hovertemplate='%{y:.1f}%<extra></extra>'
    ))
    
    # Expected line with neon effect
    fig.add_trace(go.Scatter(
        x=horizon_labels,
        y=expected,
        mode='lines+markers',
        name='Expected',
        line=dict(color='#00D4FF', width=4),
        marker=dict(size=12, color='#00D4FF', 
                    line=dict(color='#FFFFFF', width=2)),
        hovertemplate='<b>%{y:.2f}%</b><extra></extra>'
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(139, 146, 176, 0.5)", line_width=1)
    
    layout = get_plotly_layout(
        title=dict(
            text=f"<b>Projection: {ASSET_LABELS.get(asset_class, asset_class)}</b>",
            font=dict(size=18, color='#E4E8F1')
        ),
        xaxis_title="Time Horizon",
        yaxis_title="Expected Return (%)",
        height=450,
        hovermode='x unified',
        margin=dict(l=40, r=40, t=80, b=40)
    )
    fig.update_layout(layout)
    return fig


def plot_portfolio_performance(results_df, selected_events):
    """Plot portfolio performance across events."""
    fig = go.Figure()
    
    colors = ['#00D4FF', '#7C3AED', '#00F5A0', '#FFB547', '#FF3B6B', '#0066FF', '#FF6B00']
    
    for i, event_name in enumerate(selected_events):
        event_data = results_df[results_df["Event Full"] == event_name]
        if len(event_data) == 0:
            continue
        fig.add_trace(go.Scatter(
            x=event_data["Horizon"],
            y=event_data["Return (%)"],
            mode='lines+markers',
            name=event_name,
            line=dict(width=3, color=colors[i % len(colors)]),
            marker=dict(size=10, line=dict(color='#FFFFFF', width=1.5))
        ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(139, 146, 176, 0.5)")
    
    layout = get_plotly_layout(
        title=dict(
            text="<b>Portfolio Stress Test Results</b>",
            font=dict(size=18, color='#E4E8F1')
        ),
        xaxis_title="Time Horizon",
        yaxis_title="Portfolio Return (%)",
        height=500,
        hovermode='x unified',
        margin=dict(l=40, r=40, t=80, b=40)
    )
    fig.update_layout(layout)
    return fig


def plot_macro_gauge(value, label, min_val=0, max_val=10, threshold_low=3, threshold_high=7):
    """Modern gauge chart for macro indicators."""
    # Determine color based on value
    if value <= threshold_low:
        color = "#00F5A0"
    elif value >= threshold_high:
        color = "#FF3B6B"
    else:
        color = "#00D4FF"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': label, 'font': {'color': '#E4E8F1', 'size': 14}},
        number={'font': {'color': '#E4E8F1', 'size': 36, 'family': 'JetBrains Mono'}, 
                'suffix': '%'},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickcolor': '#8B92B0',
                     'tickfont': {'color': '#8B92B0'}},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': 'rgba(19, 24, 54, 0.5)',
            'borderwidth': 2,
            'bordercolor': '#2A3158',
            'steps': [
                {'range': [min_val, threshold_low], 'color': 'rgba(0, 245, 160, 0.1)'},
                {'range': [threshold_low, threshold_high], 'color': 'rgba(0, 212, 255, 0.1)'},
                {'range': [threshold_high, max_val], 'color': 'rgba(255, 59, 107, 0.1)'}
            ],
            'threshold': {
                'line': {'color': '#FFFFFF', 'width': 3},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        height=250,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def plot_correlation_matrix(data_dict):
    """Correlation matrix heatmap."""
    df = pd.DataFrame(data_dict)
    corr = df.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale=[
            [0, '#FF3B6B'],
            [0.5, '#131836'],
            [1, '#00D4FF']
        ],
        zmid=0,
        zmin=-1,
        zmax=1,
        text=corr.round(2).values,
        texttemplate="%{text}",
        textfont={"size": 10, "color": "#E4E8F1"}
    ))
    
    layout = get_plotly_layout(
        title="<b>Asset Correlation Matrix</b>",
        height=500
    )
    fig.update_layout(layout)
    return fig
def plot_multi_asset_heatmap_with_quality(impacts, event_id, data_quality=None):
    """Heatmap with quality indicators — real data shown solid, estimates shown muted."""
    event_impacts = impacts.get(event_id, {})
    horizons = ["1m", "3m", "6m", "1y", "2y"]
    
    data = []
    assets = []
    quality_data = []
    
    event_quality = (data_quality or {}).get(event_id, {})
    
    for asset, values in event_impacts.items():
        row = [values.get(h) for h in horizons]
        if any(v is not None for v in row):
            data.append(row)
            from src.data_loader import ASSET_LABELS
            assets.append(ASSET_LABELS.get(asset, asset))
            
            # Track quality for each cell
            asset_q = event_quality.get(asset, {})
            quality_row = [asset_q.get(h, "unknown") for h in horizons]
            quality_data.append(quality_row)
    
    # Build text with quality marker
    text_data = []
    for row, q_row in zip(data, quality_data):
        text_row = []
        for v, q in zip(row, q_row):
            if v is None:
                text_row.append("—")
            else:
                # Marker: solid for real, dot for estimated
                marker = "" if q in ("real", "curated") else " *"
                text_row.append(f"{v:+.1f}{marker}")
        text_data.append(text_row)
    
    custom_colorscale = [
        [0, '#FF3B6B'],
        [0.25, '#8B1A3C'],
        [0.5, '#0A1628'],
        [0.75, '#0088AA'],
        [1, '#00F5A0']
    ]
    
    import plotly.graph_objects as go
    from src.styles import get_plotly_layout
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=["1M", "3M", "6M", "1Y", "2Y"],
        y=assets,
        colorscale=custom_colorscale,
        zmid=0,
        text=text_data,
        texttemplate="%{text}",
        textfont={"size": 10, "family": "JetBrains Mono", "color": "#E4E8F1"},
        hoverongaps=False,
        colorbar=dict(
            title=dict(text="Return %", font=dict(color="#E4E8F1")),
            tickfont=dict(color="#8B92B0"),
            bgcolor="rgba(0, 8, 20, 0.6)",
            bordercolor="rgba(30, 42, 63, 0.6)",
            borderwidth=1
        )
    ))
    
    layout = get_plotly_layout(
        title=dict(
            text="<b>ASSET CLASS IMPACT MATRIX</b><br><span style='font-size:10px;color:#8B92B0'>* = estimated value</span>",
            font=dict(size=14, color='#E4E8F1', family='JetBrains Mono')
        ),
        xaxis_title="TIME HORIZON",
        height=max(550, len(assets) * 22),
        margin=dict(l=160, r=40, t=80, b=40)
    )
    fig.update_layout(layout)
    return fig