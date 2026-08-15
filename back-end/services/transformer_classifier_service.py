import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class TransformerClassifierService:

    """
    Manual zero-shot document classifier.

    This does what pipeline("zero-shot-classification") does internally:
    1. Convert each label into a hypothesis
    2. Tokenize document + hypothesis
    3. Run model
    4. Get logits
    5. Apply softmax
    6. Take entailment score
    7. Pick best label
    """

    def __init__(self):

        self.model_name = "facebook/bart-large-mnli"

        self.tokenizer= AutoTokenizer.from_pretrained(
            self.model_name
        )

        self.model= AutoModelForSequenceClassification.from_pretrained(
            self.model_name
        )

        self.candidate_labels = [
            "research paper",
            "tutorial",
            "documentation",
            "blog article",
            "news article",
            "resume",
            "technical report",
            "general article"
        ]

        self.max_characters=3000

        self.label2id = {
            label.lower(): index
            for label,index in self.model.config.label2id.items()
        }

        self.entailment_index = self.label2id["entailment"]

    def classify_documents(
        self,
        text:str
    ):

        if not text or not text.strip():
            return {
                "document_type": "unknown",
                "confidence": 0.0,
                "all_scores": []
            }

        premise = text[: self.max_characters]

        label_scores= []

        for label in self.candidate_labels:

            hypothesis = f"This text is about {label}."

            encoded_input = self.tokenizer(
                premise,
                hypothesis,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )    

            with torch.no_grad():

                outputs= self.model(
                    input_ids=encoded_input["input_ids"],
                    attention_mask=encoded_input["attention_mask"]
                )

                logits=outputs.logits

                probabilities= torch.softmax(
                    logits,
                    dim=1
                )

                entailment_score = probabilities[0][self.entailment_index].item()

                label_scores.append(
                    {
                        "label": label,
                        "score": round(float(entailment_score), 4)
                    }
                )

        scores_tensor = torch.tensor(
            [
                item["score"]
                for item in label_scores
            ]
        )

        best_label_index = torch.argmax(
            scores_tensor,
            dim=0
        ).item()

        top_result = label_scores[best_label_index]

        label_scores = sorted(
            label_scores,
            key=lambda item: item["score"],
            reverse=True
        )

        confidence_threshold = 0.50

        if top_result["score"] < confidence_threshold:
            document_type = "uncertain"
        else:
            document_type = top_result["label"]

        return {
            "document_type": document_type,
            "best_predicted_label": top_result["label"],
            "confidence": top_result["score"],
            "all_scores": label_scores
        }