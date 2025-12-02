from flask import Blueprint, request, jsonify, current_app
import uuid
import base64
import time

intake_bp = Blueprint('intake', __name__)

def get_mem(): return current_app.mem
def get_vision(): return current_app.vision
def get_fabric(): return current_app.fabric

@intake_bp.route('/detect', methods=['POST'])
def detect_items():
    print("DEBUG: Entering detect_items")
    if 'image' not in request.files:
        print("DEBUG: No image in request.files")
        return jsonify({"error": "No image uploaded"}), 400
        
    try:
        file = request.files['image']
        print(f"DEBUG: File received: {file.filename}")
        image_bytes = file.read()
        print(f"DEBUG: File read, bytes: {len(image_bytes)}")
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        print("DEBUG: Base64 encoded")
        
        # Call Vision Agent
        print("DEBUG: Calling VisionAgent.analyze_image...")
        # VisionAgent.analyze_image returns a list of dicts with bbox, type, color
        items = get_vision().analyze_image(image_b64)
        print(f"DEBUG: VisionAgent returned {len(items)} items")
        
        # Normalize output for UI
        # UI expects: items: [{label, confidence, box}]
        # VisionAgent returns: [{type, confidence, bbox, color}]
        ui_items = []
        for item in items:
            ui_items.append({
                "label": f"{item.get('color', '')} {item.get('type', 'item')}".strip(),
                "confidence": item.get('confidence', 0.9),
                "box": item.get('bbox', [0,0,0,0]), # [ymin, xmin, ymax, xmax] or similar
                "raw": item
            })
            
        return jsonify({"items": ui_items, "image_b64": image_b64})
    except Exception as e:
        import traceback
        print(f"Intake API Error: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@intake_bp.route('/analyze_fabric', methods=['POST'])
def analyze_fabric():
    data = request.json
    image_b64 = data.get('image_b64')
    hints = data.get('hints', {}) # {type: 'shirt', color: 'blue'}
    
    # Call Fabric Expert
    fabric_type, care = get_fabric().analyze(image_b64, hints)
    
    return jsonify({
        "fabric_type": fabric_type,
        "care_instructions": care
    })

@intake_bp.route('/create_order', methods=['POST'])
def create_order():
    data = request.json
    phone = data.get('phone')
    items = data.get('items')
    total = data.get('total')
    overlay_base64 = data.get('overlay_image', '')
    
    order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"
    
    # Save overlay image as file if provided
    overlay_url = f'/static/overlays/{order_id}.png'
    if overlay_base64 and overlay_base64.startswith('data:image'):
        try:
            # Remove data:image/png;base64, prefix
            image_data = overlay_base64.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            
            # Save to file
            import os
            static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'overlays')
            os.makedirs(static_dir, exist_ok=True)
            
            file_path = os.path.join(static_dir, f'{order_id}.png')
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
        except Exception as e:
            print(f"Error saving overlay image: {e}")
            overlay_url = 'https://via.placeholder.com/150?text=No+Image'
    else:
        overlay_url = 'https://via.placeholder.com/150?text=No+Image'
    
    order_data = {
        "items": items,
        "total": total,
        "timestamp": time.time(),
        "overlay_url": overlay_url
    }
    
    # Save to MemoryBank
    get_mem().save_order(order_id, phone, "Pending", order_data)
    
    return jsonify({"status": "success", "order_id": order_id})
