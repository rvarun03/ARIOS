from spacy.tokens import Doc

class NER:
    def extract(
            self,
            doc:Doc,
            max_entities: int | None = None
        ):

        entities=[]
        
        for entity in doc.ents :
            entities.append(
                {
                    "text": entity.text,
                    "label": entity.label_,
                    "start": entity.start_char,
                    "end": entity.end_char
                }
            )

        if max_entities is not None:
            return entities[:max_entities]
        
        return entities    