from flask import Blueprint, request, jsonify
import __main__

customer_bp = Blueprint('customer', __name__)

def get_mem():
    return __main__.mem

def get_offer():
    return __main__.offer

@customer_bp.route('/check_user', methods=['POST'])
def check_user():
    data = request.json
    phone = data.get('phone')
    if not phone:
        return jsonify({"error": "Phone required"}), 400
        
    profile = get_mem().get_customer(phone)
    if profile:
        return jsonify({"exists": True, "profile": profile})
    else:
        return jsonify({"exists": False})

@customer_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    phone = data.get('phone')
    name = data.get('name')
    
    if not phone:
        return jsonify({"error": "Phone required"}), 400
        
    # Save customer
    get_mem().save_customer(phone, {"name": name, "address": data.get("address")})
    
    # Generate first time code
    code = get_offer().generate_first_time_code(phone)
    
    return jsonify({"status": "registered", "code": code})

@customer_bp.route('/orders/<phone>', methods=['GET'])
def get_orders(phone):
    # Fetch real orders from shared DB
    orders = get_mem().get_orders_by_phone(phone)
    return jsonify({"orders": orders})

@customer_bp.route('/offers/<phone>', methods=['GET'])
def get_offers(phone):
    # Get existing codes from memory
    codes = get_mem().get_redeems_by_phone(phone)
    
    # Only call Offer Agent if no active (unused) offers exist
    has_active = any(not c.get('used', False) for c in codes)
    
    if not has_active:
        # Trigger Offer Agent to potentially generate a NEW personalized offer
        get_offer().generate_personalized_offer(phone)
        # Re-fetch to include the new one
        codes = get_mem().get_redeems_by_phone(phone)
    
    return jsonify({"offers": codes})
