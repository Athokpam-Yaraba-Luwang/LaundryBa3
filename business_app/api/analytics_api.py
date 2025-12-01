from flask import Blueprint, request, jsonify
import __main__

analytics_bp = Blueprint('analytics', __name__)

def get_mem(): return __main__.mem
def get_a2a(): return __main__.a2a

@analytics_bp.route('/swarm', methods=['GET'])
async def get_summary():
    timeframe = request.args.get('timeframe', 'last_7_days')
    summary = await get_a2a().call_agent("analytics_orchestrator", {"timeframe": timeframe})
    return jsonify(summary)

@analytics_bp.route('/stats', methods=['GET'])
def get_stats():
    orders = get_mem().get_all_orders()
    feedback = get_mem().get_all_feedback()
    
    # Calculate Revenue
    revenue = sum(o.get('total', 0) for o in orders)
    
    # Calculate Status Counts
    status_counts = {"Pending": 0, "Finished": 0, "Delivered": 0}
    for o in orders:
        s = o.get('status', 'Pending')
        status_counts[s] = status_counts.get(s, 0) + 1
        
    # Calculate Satisfaction
    ratings = [f['rating'] for f in feedback]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
    
    # Calculate Top Category (Simple heuristic from items)
    categories = {}
    for o in orders:
        for item in o.get('items', []):
            label = item.get('label', 'Unknown')
            # Simple extraction: "Blue Shirt" -> "Shirt"
            cat = label.split()[-1] 
            categories[cat] = categories.get(cat, 0) + 1
            
    top_category = max(categories, key=categories.get) if categories else "None"
    top_cat_pct = 0
    if categories:
        total_items = sum(categories.values())
        top_cat_pct = int((categories[top_category] / total_items) * 100)
        
    # Calculate Rating Distribution
    rating_counts = [0] * 5
    for r in ratings:
        if 1 <= r <= 5:
            rating_counts[r-1] += 1

    # Revenue Trend (Last 10 orders)
    # Assuming orders are sorted by timestamp desc, take first 10 and reverse
    rev_trend = [o.get('total', 0) for o in orders[:10][::-1]]

    return jsonify({
        "revenue": revenue,
        "orders_finished": status_counts.get('Finished', 0) + status_counts.get('Delivered', 0),
        "orders_pending": status_counts.get('Pending', 0),
        "satisfaction": round(avg_rating, 1),
        "review_count": len(ratings),
        "top_category": top_category,
        "top_category_pct": top_cat_pct,
        "chart_data": {
            "revenue_trend": rev_trend,
            "status_counts": status_counts,
            "category_counts": categories,
            "rating_counts": rating_counts
        }
    })
