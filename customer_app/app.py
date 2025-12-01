import os
import sys
import logging
from flask import Flask, render_template, redirect

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
from agents.a2a_dispatcher import A2ADispatcher
from agents.memory_bank import MemoryBank
from agents.offer_agent import OfferAgent
from agents.notification_agent import NotificationAgent

# Initialize Agents
a2a = A2ADispatcher()
mem = MemoryBank()
offer = OfferAgent(mem, a2a)
notification = NotificationAgent()

# Register notification agent
a2a.register("notification_agent", notification)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY_CUSTOMER

# Attach services to app for blueprint access
app.mem = mem
app.a2a = a2a
app.offer = offer

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
    business_url = Config.BUSINESS_APP_URL
    return render_template('my_orders.html', business_url=business_url)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', Config.PORT_CUSTOMER))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
