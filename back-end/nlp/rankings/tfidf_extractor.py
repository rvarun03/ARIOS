from sklearn.feature_extraction.text import TfidfVectorizer

class TFIDFExtractor:

    def __init__(
            self,
            max_features: int =20
        ):

        self.max_features =max_features

    def extract(
            self,
            text:str
        ) -> list[dict] :

        if not text:
            return []
        
        vectorizer= TfidfVectorizer(
            stop_words="english",
            max_features=self.max_features,
            ngram_range=(1,2)
        )

        tfidf_matrix=vectorizer.fit_transform(
            [text]
        )

        feature_names= (
            vectorizer.get_feature_names_out()
        )

        scores=(
            tfidf_matrix.toarray()[0]
        )

        ranked_terms= sorted(
            zip(feature_names, scores),
            key= lambda x:x[1],
            reverse=True
        )

        return [
            {
                "term": term,
                "score": round(score,4)
            }
            for term, score in ranked_terms
            if not term.isdigit()
        ]


