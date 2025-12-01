import os
import sys
import logging
from flask import Flask, render_template, redirect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path to import agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.a2a_dispatcher import A2ADispatcher
from agents.memory_bank import MemoryBank
from agents.offer_agent import OfferAgent
from agents.notification_agent import NotificationAgent

# Initialize Agents (Global for demo)
# Note: In a real distributed system, these would be separate services or share a DB.
# For this local demo, we are re-instantiating them, which means IN-MEMORY state won't share.
# However, MemoryBank uses SQLite, so state WILL share if they point to the same DB file.
a2a = A2ADispatcher()
mem = MemoryBank() # Defaults to agents_memory.db in CWD
offer = OfferAgent(mem, a2a)
notification = NotificationAgent()

# Register notification agent so offers can send notifications
a2a.register("notification_agent", notification)

app = Flask(__name__)
app.secret_key = "cust_key"

# Import APIs
from api.customer_api import customer_bp
from api.feedback_api import feedback_bp

app.register_blueprint(customer_bp, url_prefix='/api/customer')
app.register_blueprint(feedback_bp, url_prefix='/api/feedback')

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/my_orders')
def my_orders():
    business_url = os.environ.get('BUSINESS_APP_URL', 'http://localhost:5000')
    return render_template('my_orders.html', business_url=business_url)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
