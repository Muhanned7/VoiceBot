import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer
from torch.utils.data import Dataset
import torch
from utils.logger import get_logger


logger = get_logger(__name__)

MODEL_NAME = "bert-base-uncased"
MAX_LENGTH = 64

# maps intent string labels to numbers and back
INTENT_LABELS = [
    "order_status",
    "order_cancellation",
    "refund_request",
    "subscription_issue",
    "password_reset",
    "shipping_query",
    "product_inquiry",
    "account_issue",
    "payment_issue",
    "return_request",
    "complaint",
    "general_inquiry"
]

LABEL2ID = {label: idx for idx, label in enumerate(INTENT_LABELS)}
ID2LABEL = {idx: label for idx, label in enumerate(INTENT_LABELS)}

class IntentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="pt"
        )
        self.labels = torch.tensor(labels)
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return {
            "input_ids": self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels": self.labels[idx]
        }
    
def load_dataset(csv_path: str):
    logger.info(f"Loading dataset from {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Total examples: {len(df)}")

    # convert string labels to numbers
    df["label_id"] = df["intent"].map(LABEL2ID)

    texts = df["text"].tolist()
    labels = df["label_id"].tolist()

    # split into train and eval
    train_texts, eval_texts, train_labels, eval_labels = train_test_split(
        texts, labels,
        test_size=0.2,
        random_state=42,
        stratify=labels        # ensures each intent is equally represented in both splits
    )

    logger.info(f"Train: {len(train_texts)} | Eval: {len(eval_texts)}")

    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

    train_dataset = IntentDataset(train_texts, train_labels, tokenizer)
    eval_dataset = IntentDataset(eval_texts, eval_labels, tokenizer)

    return train_dataset, eval_dataset, tokenizer

