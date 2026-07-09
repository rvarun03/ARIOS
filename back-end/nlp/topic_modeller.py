from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

class TopicModeller:
    """
    Traditional Topic Modeling using TF-IDF + NMF.

    Goal:
    - Take multiple documents
    - Convert them into numbers using TF-IDF
    - Discover hidden topics using NMF
    - Assign each document to its strongest topic

    """
    
    def __init__(
        self,
        num_topics: int = 3,
        top_n_words: int = 10,
        max_features: int = 1000
    ):
        self.num_topics = num_topics
        self.top_n_words = top_n_words
        self.max_features = max_features


    def fit_transform(
        self,
        documents: list[str],
        titles: list[str] | None = None
    ) -> dict:

        if not documents:
            return {
                "topics": [],
                "documents": [],
                "warning": "No documents provided"
            }

        # Keep documents and titles aligned
        cleaned_items = []

        for index, document in enumerate(documents):

            if document and document.strip():

                title = (
                    titles[index]
                    if titles and index < len(titles)
                    else f"Document {index + 1}"
                )

                cleaned_items.append(
                    {
                        "title":title,
                        "text": document
                    }
                )

        if not cleaned_items:
            return {
                "topics": [],
                "documents": [],
                "warning": "All documents were empty"
            }

        cleaned_documents=[
            item["text"] 
            for item in cleaned_items
        ]            

        cleaned_titles = [
            item["title"]
            for item in cleaned_items
        ]

        # Step 1: Convert text into TF-IDF matrix

        vectorizer= TfidfVectorizer(
            stop_words="english",
            max_features=self.max_features,
            ngram_range=(1,2),
            min_df=1
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(
                cleaned_documents
            )

        except ValueError as error:
            return {
                "topics": [],
                "documents": [],
                "warning": str(error)
            }
        
        feature_names= vectorizer.get_feature_names_out()

        # Step 2: Decide how many topics are actually possible
        
        effective_topics= min(
            self.num_topics,
            tfidf_matrix.shape[0],
            tfidf_matrix.shape[1]
        )

        if effective_topics <= 0:
            return {
                "topics": [],
                "documents": [],
                "warning": "Not enough data to build topics"
            }
        
        # Step 3: Apply NMF
        model = NMF(
            n_components=effective_topics,
            random_state=42,
            init="nndsvda",
            max_iter=500
        )

        document_topic_matrix= model.fit_transform(
            tfidf_matrix
        )

        # Step 4: Extract top words for each topic
        topics = []

        for topic_index,topic_weights in enumerate(
            model.components_
        ):
            topic_word_indices=(
                topic_weights
                .argsort()[::-1][:self.top_n_words]
            )

            top_words=[]

            for word_index in topic_word_indices:

                top_words.append(
                    {
                        "word": feature_names[word_index],
                        "weight": round(
                            float(topic_weights[word_index]),
                            4
                        )
                    }
                )    

            topics.append(
                {
                    "topic_id": topic_index,
                    "label": ", ".join(
                        item["word"]
                        for item in top_words[:3]
                    ),
                    "top_words": top_words
                }
            )  

        #Step-5 Assign dominant topic to each document
        document_topics=[]

        for document_index, topic_scores in enumerate(
            document_topic_matrix
        ):
            dominant_topic_id = int(
                topic_scores.argmax()
            )

            document_topics.append(
                {
                    "title": cleaned_titles[document_index],
                    "dominant_topic_id": dominant_topic_id,
                    "dominant_topic_label": topics[dominant_topic_id]["label"],
                    "topic_score": round(
                        float(topic_scores[dominant_topic_id]),
                        4
                    )
                }
            )

        warning = None

        if len(cleaned_documents) < 3:
            warning = (
                "Topic modeling works better with multiple documents. "
                "Current result is valid but may be weak."
            )

        return {
            "topics": topics,
            "documents": document_topics,
            "matrix_info": {
                "document_count": tfidf_matrix.shape[0],
                "vocabulary_size": tfidf_matrix.shape[1],
                "topic_count": effective_topics
            },
            "warning": warning
        }    