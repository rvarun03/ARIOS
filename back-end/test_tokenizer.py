from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "facebook/bart-large-mnli"

tokenizer = AutoTokenizer.from_pretrained(
    model_name
)

model = AutoModelForSequenceClassification.from_pretrained(
    model_name
)

premise = """
This guide explains how to build REST APIs using FastAPI,
SQLAlchemy, JWT authentication, and database models.
"""

candidate_labels = [
    "research paper",
    "tutorial",
    "documentation",
    "blog article",
    "news article",
    "resume",
    "technical report",
    "general article"
]

label_scores=[]

for label in candidate_labels:

    hypothesis = f"This text is about {label}."

    encoded_input = tokenizer(
        premise,
        hypothesis,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )

    with torch.no_grad():

        outputs= model(
            input_ids=encoded_input["input_ids"],
            attention_mask=encoded_input["attention_mask"]
        )

        logits=outputs.logits

        probabilities=torch.softmax(
            logits,
            dim=1
        )

        label_mapping = model.config.id2label

        print("\nLABEL BEING CHECKED:", label)
        print("HYPOTHESIS:", hypothesis)
        print("LOGITS:", logits)
        print("PROBABILITIES:", probabilities)
        print("MODEL LABEL MAPPING:", label_mapping) 

        entailment_score = probabilities[0][2].item()

        label_scores.append(
            {
                "label": label,
                "score": round(float(entailment_score),4)
            }
        )

label_scores = sorted(
    label_scores,
    key=lambda item: item["score"],
    reverse=True
)

print("\nFINAL ZERO-SHOT RESULT:")
print(label_scores)

best_label = label_scores[0]

print("\nBEST LABEL:")
print(best_label["label"])

print("\nCONFIDENCE:")
print(best_label["score"])