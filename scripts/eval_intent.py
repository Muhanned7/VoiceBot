import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)
from core.intent.classifier import IntentClassifier
from core.intent.dataset import INTENT_LABELS

classifier = IntentClassifier()
classifier.load()

df = pd.read_csv("data/raw/intents.csv")
texts = df["text"].tolist()
true_labels = df["intent"].tolist()

print("\n--- Intent Evaluation ---\n")

predicted_labels = []

for text in texts:
    try:
        result = classifier.predict(text)
        predicted_labels.append(result["intent"])
    except Exception:
        predicted_labels.append("general_inquiry")

accuracy = accuracy_score(true_labels, predicted_labels)
precision, recall, f1, _ = precision_recall_fscore_support(
    true_labels, predicted_labels, average="weighted", zero_division=0
)

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")
print()
print(classification_report(true_labels, predicted_labels, zero_division=0))

cm = confusion_matrix(true_labels, predicted_labels, labels=INTENT_LABELS)

plt.figure(figsize=(12, 10))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    xticklabels=INTENT_LABELS,
    yticklabels=INTENT_LABELS,
    cmap="Blues"
)
plt.title("Intent Classifier — Confusion Matrix")
plt.ylabel("True Label")
plt.xlabel("Predicted Label")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
print("Confusion matrix saved to confusion_matrix.png")
