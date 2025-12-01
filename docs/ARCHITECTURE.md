# LaundryBa Enterprise Architecture

## Overview
LaundryBa Enterprise is a comprehensive laundry management system consisting of two main applications and a shared backend infrastructure powered by AI agents.

## Components

### 1. Business App
- **Purpose**: Manage laundry intake, operations, analytics, and offers.
- **Tech Stack**: Flask, HTML/CSS/JS, Google Cloud Run.
- **Key Modules**:
    - **Customer DB**: Manage customer profiles and orders.
    - **Smart Intake**: AI-powered order creation (Vision + Fabric Expert).
    - **Analytics Forms**: On-demand business insights.
    - **Visualizations**: Real-time KPI dashboard.
    - **Redeem/Offers**: Manage offers and codes.

### 2. Customer App
- **Purpose**: Customer interface for registration, tracking orders, and offers.
- **Tech Stack**: Flask, HTML/CSS/JS, Google Cloud Run.
- **Key Modules**:
    - **Registration & Profile**: Phone-based identity.
    - **Offers**: View and redeem codes.
    - **My Laundry**: Track order status with AI overlays.
    - **Feedback**: Submit ratings and reviews.

### 3. AI Agents Layer
- **Orchestration**: A2A Dispatcher (Local/ADK).
- **Agents**:
    - **Vision Agent**: Item detection and classification.
    - **Fabric Expert**: Fabric analysis and care instructions.
    - **HITL Agent**: Human-in-the-loop verification.
    - **Offer Agent**: Personalized offer generation.
    - **Notification Agent**: Push notifications.
    - **Analytics Agents**: Revenue, Logistics, Feedback analysis.

### 4. Data Layer
- **Database**: Google Cloud SQL / Firestore (Shared).
- **Storage**: Google Cloud Storage (Images).

## Integration
- **A2A**: Agents communicate via a dispatcher.
- **Shared DB**: Both apps read/write to the same database for real-time sync.
- **MCP**: Model Context Protocol for tool integration.
