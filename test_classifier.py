from core.intent.classifier import IntentClassifier

classifier = IntentClassifier()
classifier.load()

tests = [
    'I want a refund',
    'reset my password',
    'my payment failed',
    'cancel my order'
]

for text in tests:
    result = classifier.predict(text)
    print(f'{text:<30} → {result["intent"]:<25} ({result["confidence"]})')