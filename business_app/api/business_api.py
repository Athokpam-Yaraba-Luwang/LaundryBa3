from flask import Blueprint, request, jsonify
import __main__

business_bp = Blueprint('business', __name__)

def get_mem(): return __main__.mem
def get_a2a(): return __main__.a2a

@business_bp.route('/customers', methods=['GET'])
def get_customers():
    # Get all customers
    customers = get_mem().get_all_customers()
    # For each customer, get order count
    for c in customers:
        orders = get_mem().get_orders_by_phone(c['phone'])
        c['orders_count'] = len(orders)
    return jsonify({"customers": customers})

@business_bp.route('/orders/<phone>', methods=['GET'])
def get_customer_orders(phone):
    orders = get_mem().get_orders_by_phone(phone)
    return jsonify({"orders": orders})

@business_bp.route('/order/update_status', methods=['POST'])
def update_status():
    data = request.json
    order_id = data.get('id')
    status = data.get('status')
    phone = data.get('phone')
    
    get_mem().update_order_status(order_id, status)
    
    # Trigger Notification Agent
    if status in ['Finished', 'Delivered']:
        msg = f"Your order {order_id} is now {status}!"
        get_a2a().call_agent("notification_agent", {"phone": phone, "msg": msg})
        
    return jsonify({"status": "updated"})

@business_bp.route('/redeem_codes', methods=['GET'])
def get_redeem_codes():
    codes = get_mem().get_all_redeems()
    return jsonify({"codes": codes})
