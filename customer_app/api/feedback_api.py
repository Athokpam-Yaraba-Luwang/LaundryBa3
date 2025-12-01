from flask import Blueprint, request, jsonify
import __main__

feedback_bp = Blueprint('feedback', __name__)

def get_mem():
    return __main__.mem

@feedback_bp.route('/submit', methods=['POST'])
def submit_feedback():
    data = request.json
    order_id = data.get('order_id', 'GENERIC')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    # Save feedback to database
    import uuid
    feedback_id = str(uuid.uuid4())
    get_mem().save_feedback(feedback_id, order_id, rating, comment)
    
    print(f"Feedback received for {order_id}: {rating} stars - {comment}")
    
    return jsonify({"status": "received", "thank_you": True})
