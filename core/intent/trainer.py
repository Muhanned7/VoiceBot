from transformers import DataCollatorWithPadding, BertForSequenceClassification, TrainingArguments, Trainer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
import torch
from core.intent.dataset import load_dataset, INTENT_LABELS, ID2LABEL, LABEL2ID
from utils.logger import get_logger


logger = get_logger(__name__)

MODEL_NAME = "bert-base-uncased"
MODEL_SAVE_PATH = "models/intent_classifier"


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=1)

    accuracy = accuracy_score(labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average="weighted"
    )

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }

def train(csv_path: str = "data/raw/intents.csv"):
    logger.info("Starting intent classifier training")

    train_dataset, eval_dataset, tokenizer = load_dataset(csv_path)

    model = BertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(INTENT_LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID
    )

    training_args = TrainingArguments(
        output_dir=MODEL_SAVE_PATH,
        num_train_epochs=5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_dir="logs",
        logging_steps=10,
    )
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics,
        data_collator=data_collator,
    )

    logger.info("Training started")
    trainer.train()

    logger.info(f"Saving model to {MODEL_SAVE_PATH}")
    trainer.save_model(MODEL_SAVE_PATH)
    tokenizer.save_pretrained(MODEL_SAVE_PATH)
    logger.info("Training complete")


if __name__ == "__main__":
    train()  