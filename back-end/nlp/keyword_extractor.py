from spacy.tokens import Doc
from collections import Counter

class KeywordExtractor:
    
    IMPORTANT_POS = {
        "NOUN",
        "PROPN",
        "ADJ"
    }

    def extract(
        self,
        doc:Doc,
        top_n: int = 50
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

        keyword_counts = Counter(
            keywords
        )

        return [
            {
                "keyword": keyword,
                "count": count
            }
            for keyword, count in keyword_counts.most_common(top_n)
        ]
            