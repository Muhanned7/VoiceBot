from transformers import BertForSequenceClassification, BertTokenizer
import torch
from utils.logger import get_logger
from utils.exceptions import ModelNotLoaded, LowConfidenceIntent
from utils.config_loader import load_settings

logger = get_logger(__name__)

MODEL_PATH = "models/intent_classifier"

MODEL_PATH = "models/intent_classifier"
cfg = load_settings()
CONFIDENCE_THRESHOLD = cfg.intent.confidence_threshold

class IntentClassifier:

    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None

    def load(self) -> None:
        logger.info(f"Loading intent classifier from {self.model_path}")
        self.tokenizer = BertTokenizer.from_pretrained(self.model_path)
        self.model = BertForSequenceClassification.from_pretrained(self.model_path, cache_dir=cfg.cache.huggingface)
        self.model.eval()
        logger.info("Intent classifier loaded successfully")

    def predict(self, text: str) -> dict:
        if self.model is None:
            raise ModelNotLoaded("Intent classifier not loaded. Call load() first.")

        logger.info(f"Classifying: '{text}'")

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=64
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
        confidence, predicted_id = torch.max(probabilities, dim=1)

        predicted_label = self.model.config.id2label[predicted_id.item()]
        confidence_score = round(confidence.item(), 4)

        logger.info(f"Predicted: {predicted_label} ({confidence_score})")
        
        if confidence_score < CONFIDENCE_THRESHOLD:
            raise LowConfidenceIntent(predicted_label, confidence_score)

        return {
            "intent": predicted_label,
            "confidence": confidence_score
        }