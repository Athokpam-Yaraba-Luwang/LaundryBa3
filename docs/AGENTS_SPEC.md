# AI Agents Specification

## 1. Vision Agent
- **Input**: Image (Base64/URL).
- **Output**: List of detections (bbox, type, color, confidence).
- **Tech**: Gemini Vision / Google Cloud Vision.

## 2. Fabric Expert Agent
- **Input**: Image crop, hints (type, color).
- **Output**: Fabric type, Care instructions.
- **Tech**: Self-evolving knowledge base + Google Search Tool.

## 3. Offer Agent
- **Input**: Customer ID/Phone.
- **Output**: Redeem code, Discount details.
- **Logic**: Analyzes spending patterns, frequency, and feedback to generate personalized offers.

## 4. HITL Agent
- **Purpose**: Verification of AI outputs (e.g., bounding boxes).
- **Flow**: Agent creates a task -> Admin verifies/edits -> Agent resumes.

## 5. Notification Agent
- **Purpose**: Send updates to customers.
- **Triggers**: Order status change, New offer.

## 6. Analytics Agents
- **Revenue Agent**: Analyzes revenue trends.
- **Logistics Agent**: Analyzes turnaround time, bottlenecks.
- **Feedback Agent**: Analyzes customer sentiment and common issues.
