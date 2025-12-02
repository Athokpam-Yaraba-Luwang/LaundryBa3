# agents/vision_agent.py
import base64, logging, uuid, os
from typing import List, Dict

logger = logging.getLogger("vision_agent")

# Check for API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# agents/vision_agent.py

from google.adk import Agent, AgentConfig
from google.adk.tools import ToolContext
from google import genai
import base64
import json
import asyncio

class VisionAgent(Agent):
    def __init__(self):
        super().__init__(
            config=AgentConfig(
                name="vision_agent",
                model="gemini-2.0-flash-exp",
                description="Detects clothes and returns bounding boxes + attributes",
                system_instruction="""
                You are a vision agent for a laundry business.
                You're given an image and must detect:
                - cloth type (shirt, blanket, pants, socks)
                - bounding boxes
                - color
                - confidence score
                
                IMPORTANT: This image is 1:1 aspect ratio (square).
                Return a JSON list where each item has:
                - type: (shirt/pants/towel/socks/etc)
                - color: (color of the item)
                - bbox: [ymin, xmin, ymax, xmax] in NORMALIZED coordinates (0.0 to 1.0 scale).
                
                Example format:
                [
                    {"type": "shirt", "color": "blue", "bbox": [0.1, 0.2, 0.45, 0.6]},
                    {"type": "pants", "color": "black", "bbox": [0.5, 0.25, 0.85, 0.65]}
                ]
                """,
            )
        )

        self.client = genai.Client()

    async def handle(self, ctx: ToolContext):
        img_b64 = ctx.inputs["image_b64"]
        
        # Decode base64 to bytes for Gemini
        # Note: The shim/client handles the format conversion
        import PIL.Image
        import io
        
        try:
            img_bytes = base64.b64decode(img_b64)
            image = PIL.Image.open(io.BytesIO(img_bytes))
            
            system_instruction = """
            You are a vision agent for a laundry business.
            You're given an image and must detect:
            - cloth type (shirt, blanket, pants, socks)
            - bounding boxes
            - color
            - confidence score
            
            Return a JSON list where each item has:
            - type: (shirt/pants/towel/socks/etc)
            - color: (color of the item)
            - bbox: [ymin, xmin, ymax, xmax] in NORMALIZED coordinates (0.0 to 1.0 scale).
              * ymin: top edge
              * xmin: left edge
              * ymax: bottom edge
              * xmax: right edge
            
            Example format:
            [
                {"type": "shirt", "color": "blue", "bbox": [0.1, 0.2, 0.45, 0.6]},
                {"type": "pants", "color": "black", "bbox": [0.5, 0.25, 0.85, 0.65]}
            ]
            """
            prompt = f"{system_instruction}\n\nDetect clothing items and return JSON."
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[{"role":"user","parts":[{"image": image, "text": prompt}]}]
            )

            # Parse response
            text = response.text
            # Clean up markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
                
            items = json.loads(text)
            # Add IDs
            for item in items:
                item["item_id"] = str(uuid.uuid4())
                if "confidence" not in item:
                    item["confidence"] = 0.9 # Placeholder if not provided by model
            return items
            
        except Exception as e:
            import traceback
            logger.error(f"Vision Agent Error: {e}")
            logger.error(traceback.format_exc())
            # Check if API key is set
            key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not key:
                logger.error("CRITICAL: GOOGLE_API_KEY is missing!")
            else:
                logger.info(f"API Key present (starts with {key[:4]}...)")
            raise e

    # Legacy method for backward compatibility during migration
    def analyze_image(self, image_b64: str) -> List[Dict]:
        ctx = ToolContext({"image_b64": image_b64})
        return asyncio.run(self.handle(ctx))
