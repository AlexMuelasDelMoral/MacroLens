import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from src.data_loader import ASSET_LABELS

COLORS = {
    "positive": "#10b981",
    "negative": "#ef4444",
    "neutral": "#6b7280",
    "primary": "#3b82f6",
    "warning": "#f59e0b"
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
        marker_color=colors,
        text=[f"{v:+.1f}%" if v is not None else "N/A" for v in values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f"{ASSET_LABELS.get(asset_class, asset_class)} - {event_name}",
        xaxis_title="Return (%)",
        yaxis_title="Time Horizon",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
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
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=["1M", "3M", "6M", "1Y", "2Y"],
        y=assets,
        colorscale='RdYlGn',
        zmid=0,
        text=[[f"{v:+.1f}%" if v is not None else "N/A" for v in row] for row in data],
        texttemplate="%{text}",
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title="Asset Class Impact Heatmap",
        xaxis_title="Time Horizon",
        height=500,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def plot_similarity_scores(similar_events):
    """Bar chart of similarity scores for matched events."""
    names = [item["event"]["name"] for item in similar_events]
    scores = [item["similarity"] for item in similar_events]
    years = [item["event"]["year"] for item in similar_events]
    
    fig = go.Figure(go.Bar(
        x=scores,
        y=[f"{n} ({y})" for n, y in zip(names, years)],
        orientation='h',
        marker_color=COLORS["primary"],
        text=[f"{s}%" for s in scores],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Most Similar Historical Events",
        xaxis_title="Similarity Score (%)",
        height=400,
        xaxis=dict(range=[0, 110]),
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def plot_prediction_with_uncertainty(predictions, asset_class):
    """Line chart with confidence bands for predictions."""
    horizons = ["1m", "3m", "6m", "1y", "2y"]
    horizon_labels = ["1M", "3M", "6M", "1Y", "2Y"]
    
    expected = [predictions[h]["expected"] if predictions[h] else None for h in horizons]
    mins = [predictions[h]["min"] if predictions[h] else None for h in horizons]
    maxs = [predictions[h]["max"] if predictions[h] else None for h in horizons]
    
    fig = go.Figure()
    
    # Uncertainty band
    fig.add_trace(go.Scatter(
        x=horizon_labels + horizon_labels[::-1],
        y=maxs + mins[::-1],
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Historical Range',
        showlegend=True
    ))
    
    # Expected line
    fig.add_trace(go.Scatter(
        x=horizon_labels,
        y=expected,
        mode='lines+markers',
        name='Expected',
        line=dict(color=COLORS["primary"], width=3),
        marker=dict(size=10)
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title=f"Predicted Impact: {ASSET_LABELS.get(asset_class, asset_class)}",
        xaxis_title="Time Horizon",
        yaxis_title="Expected Return (%)",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig
