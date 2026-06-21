from collections import Counter
from spacy.tokens import Doc


class DocumentAnalyzer:
    def analyse(
      self,
      doc: Doc,
      keywords: list,
      entities: list      
    ):
        entity_types= Counter(
            entity["label"]
            for entity in entities
        )
        return {
            "statistics" :{
                "word_count": len(
                    [
                        token
                        for token in doc 
                        if token.is_alpha
                    ]
                ),

                "sentence_count": len(
                    list(doc.sents)
                ),

                "entity_count": len(
                    entities
                ),        

                "keyword_count": len(
                    keywords
                )
            },

            "metadata":{
                "keywords": keywords,
                "entities": entities,
                "entity_types": dict(
                    entity_types
                )
            }
        }