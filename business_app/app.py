import os
import sys
import logging
from flask import Flask, render_template, jsonify, redirect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path to import agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.a2a_dispatcher import A2ADispatcher
# business_app/app.py

from agents.vision_agent import VisionAgent
from agents.fabric_expert_agent import FabricExpertAgent
from agents.hitl_agent import HITLAgent
from agents.offer_agent import OfferAgent
from agents.analytics_orchestrator import AnalyticsOrchestrator
from agents.notification_agent import NotificationAgent # Added import for NotificationAgent
from agents.memory_bank import MemoryBank # Added import for MemoryBank
from agents.analytics_agents import RevenueAgent, LogisticsAgent, FeedbackAgent # Real Analytics Agents

# Initialize Services
mem = MemoryBank()
a2a = A2ADispatcher()

# Initialize Agents
vision = VisionAgent()
fabric = FabricExpertAgent(mem)
hitl = HITLAgent(mem)  # Using mem as session service for demo
notification = NotificationAgent()
offer = OfferAgent(mem, a2a)
analytics = AnalyticsOrchestrator(a2a)
revenue = RevenueAgent(mem)
logistics = LogisticsAgent(mem)
feedback = FeedbackAgent(mem)

# Register Agents with Dispatcher (A2A)
# Note: In a full ADK runtime, this happens automatically via config.
# Here we manually register the handle methods or wrappers.
a2a.register("vision_agent", vision)
a2a.register("fabric_expert", fabric)
a2a.register("hitl_agent", hitl)
a2a.register("offer_agent", offer)
a2a.register("analytics_orchestrator", analytics)
a2a.register("notification_agent", notification) # Register instance directly
a2a.register("revenue_agent", revenue)
a2a.register("logistics_agent", logistics)
a2a.register("feedback_agent", feedback)


app = Flask(__name__)
app.secret_key = "dev_key"

# Attach services to app for blueprint access
app.mem = mem
app.a2a = a2a
app.vision = vision
app.fabric = fabric
app.hitl = hitl
app.offer = offer
app.analytics = analytics
app.revenue = revenue
app.logistics = logistics
app.feedback = feedback

# Import APIs
from api.intake_api import intake_bp
from api.analytics_api import analytics_bp
from api.business_api import business_bp

app.register_blueprint(intake_bp, url_prefix='/api/intake')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(business_bp, url_prefix='/api/business')

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/intake')
def intake():
    return render_template('intake.html')

@app.route('/customers')
def customers():
    return render_template('customers.html')

@app.route('/offers')
def offers():
    return render_template('offers.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
