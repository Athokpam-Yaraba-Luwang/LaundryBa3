from flask import Blueprint, request, jsonify, current_app
# import __main__ <-- Removed

customer_bp = Blueprint('customer', __name__)

def get_mem():
    return current_app.mem

def get_offer():
    return current_app.offer

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

@customer_bp.route('/notifications', methods=['GET'])
def get_notifications():
    # In a real app, get phone from session/auth
    # For demo, we'll accept a query param or default to a test user
    phone = request.args.get('phone', '123') 
    
    # We need access to MemoryBank. In customer_app/app.py, it's attached to app.
    # We can also re-instantiate it safely.
    from agents.memory_bank import MemoryBank
    mem = MemoryBank()
    notifs = mem.get_notifications_by_phone(phone)
    return jsonify({"notifications": notifs})
