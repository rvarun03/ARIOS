from spacy.tokens import Doc

class NER:
    def extract(self,doc:Doc):

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


        return entities    