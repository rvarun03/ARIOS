from spacy.tokens import Doc

class KeywordExtractor:
    
    IMPORTANT_POS = {
        "NOUN",
        "PROPN",
        "ADJ"
    }

    def extract(
        self,
        doc:Doc
    ) -> list[str]:
        
        keywords=[]

        for token in doc:

            if(
                token.pos_ in self.IMPORTANT_POS 
                and not token.is_stop
                and token.is_alpha
            ):
                keywords.append(
                    token.lemma_.lower()
                )

        return list(
            set(keywords)
        ) 
            