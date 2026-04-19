import yaml
import random
from utils.logger import get_logger

logger = get_logger(__name__)

TEMPLATES_PATH = "config/response_templates.yaml"

class ResponseGenerator:

    def __init__(self, templates_path: str = TEMPLATES_PATH):
        self.templates_path = templates_path
        self.templates = {}

    def load(self) -> None:
        logger.info(f"Loading response templates from {self.templates_path}")
        with open(self.templates_path, "r") as f:
            self.templates = yaml.safe_load(f)
        logger.info(f"Loaded templates for {len(self.templates)} intents")

    def generate(self, intent: str) -> str:
        if not self.templates:
            raise RuntimeError("Templates not loaded. Call load() first.")
        
        if intent not in self.templates:
            logger.warning(f"No template found for intent: {intent}")
            return "I am sorry, I could not find an answer to your query. Please contact support."

        responses = self.templates[intent]
        chosen = random.choice(responses)
        logger.info(f"Response for '{intent}': '{chosen[:50]}'")
        return chosen