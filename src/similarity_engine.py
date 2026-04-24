import numpy as np
from sklearn.preprocessing import StandardScaler
from src.data_loader import load_events, load_impacts

def calculate_similarity(user_conditions, event_conditions, weights=None):
    """
    Calculate similarity between user scenario and historical event.
    Uses weighted Euclidean distance converted to similarity score.
    """
    features = ["inflation", "fed_funds_rate", "unemployment", "gdp_growth"]
    
    if weights is None:
        weights = {"inflation": 1.0, "fed_funds_rate": 1.0, 
                   "unemployment": 0.8, "gdp_growth": 1.0}
    
    distance = 0
    count = 0
    for feature in features:
        user_val = user_conditions.get(feature)
        event_val = event_conditions.get(feature)
        
        if user_val is not None and event_val is not None:
            # Normalize by typical ranges
            ranges = {"inflation": 15, "fed_funds_rate": 20, 
                      "unemployment": 12, "gdp_growth": 10}
            normalized_diff = abs(user_val - event_val) / ranges[feature]
            distance += weights[feature] * normalized_diff ** 2
            count += weights[feature]
    
    if count == 0:
        return 0
    
    distance = np.sqrt(distance / count)
    # Convert to similarity (0-100)
    similarity = max(0, 100 * (1 - distance))
    return round(similarity, 1)

def find_similar_events(user_conditions, event_category=None, top_n=5):
    """Find most similar historical events based on macro conditions."""
    events = load_events()
    
    if event_category and event_category != "All":
        events = [e for e in events if e["category"] == event_category]
    
    results = []
    for event in events:
        sim = calculate_similarity(user_conditions, event["pre_conditions"])
        results.append({
            "event": event,
            "similarity": sim
        })
    
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_n]

def aggregate_impact_prediction(similar_events, asset_class):
    """
    Create weighted prediction based on similar events.
    Returns expected return at different horizons with confidence bands.
    """
    impacts = load_impacts()
    horizons = ["1m", "3m", "6m", "1y", "2y"]
    
    predictions = {}
    for horizon in horizons:
        values = []
        weights = []
        
        for item in similar_events:
            event_id = item["event"]["id"]
            similarity = item["similarity"]
            
            if event_id in impacts and asset_class in impacts[event_id]:
                val = impacts[event_id][asset_class].get(horizon)
                if val is not None:
                    values.append(val)
                    weights.append(similarity)
        
        if values:
            weights = np.array(weights)
            values = np.array(values)
            weighted_mean = np.sum(values * weights) / np.sum(weights)
            
            predictions[horizon] = {
                "expected": round(weighted_mean, 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "std": round(np.std(values), 2),
                "n_samples": len(values)
            }
        else:
            predictions[horizon] = None
    
    return predictions
