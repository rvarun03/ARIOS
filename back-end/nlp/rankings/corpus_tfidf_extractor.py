from sklearn.feature_extraction.text import (
    TfidfVectorizer
)


class CorpusTFIDFExtractor:

    def __init__(
        self,
        corpus: list[str],
        max_features: int = 100
    ):

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=max_features,
            ngram_range=(1, 2),
            token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9\-]+\b"
        )

        self.tfidf_matrix = (
            self.vectorizer.fit_transform(
                corpus
            )
        )

        self.feature_names = (
            self.vectorizer
            .get_feature_names_out()
            .tolist()
        )
    
    
    def get_document_analyser(
        self,
        document_index: int,
        top_k: int=20
    ):
        
        scores = (
            self.tfidf_matrix[document_index]
            .toarray()[0]
        )

        ranked_terms = sorted(
            zip(
                self.feature_names,
                scores
            ),
            key=lambda x: x[1],
            reverse=True
        )

        return [

            {
                "term": term,
                "score": round(float(score), 4)
            }

            for term, score in ranked_terms[:top_k]
            if score > 0
        ]

