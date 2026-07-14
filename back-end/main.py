from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
import uvicorn
from core.database import get_db
from routes.health import router as health_router

from ingestion.ingestion_router import ingest
from nlp.text_processor import TextProcessor
from nlp.pos_tagger import POSTagger
from nlp.NER import NER
from nlp.dependency_parser import DependencyParser
from nlp.keyword_extractor import KeywordExtractor
from nlp.document_analyser import DocumentAnalyzer
from nlp.rankings.tfidf_extractor import TFIDFExtractor

from nlp.topic_modeller import TopicModeller
from nlp.rankings.corpus_tfidf_extractor import CorpusTFIDFExtractor
from nlp.similarity.cosine_similarity import DocumentSimilarity
from nlp.extractive_summarizer import ExtractiveSummarizer

from services.nlp_analysis_service import NLPAnalysisService
from services.corpus_service import get_corpus


from models.document import Document
from models.document_chunk import DocumentChunk

from routes.document import router as document_router

from core.database import (
    Base,
    engine
)
from models.document import Document


app=FastAPI(title="ARIOS Backend")

Base.metadata.create_all(
    bind=engine
)

# register routes
app.include_router(health_router)
app.include_router(
    document_router
)

@app.get("/")
def root():
    return {"message": "ARIOS is running"}


# @app.get("/test/ingest")
# def test_ingest():

#     result= ingest(
#         source_type="web",
#         source="https://en.wikipedia.org/wiki/Virat_Kohli"
#     )

#     processor=TextProcessor()
#     pos_tagger = POSTagger()
#     ner_extractor = NER()
#     parser = DependencyParser()
#     keyword_extractor = KeywordExtractor()
#     document_analyser=DocumentAnalyzer()
#     tf_idf_extractor=TFIDFExtractor()

#     cleaned_text = processor.clean_text(
#         result.raw_text
#     )

#     normalised_text=processor.normalize_text(cleaned_text)

#     doc = processor.tokenize(normalised_text)


    
#     filtered_tokens = processor.remove_stopwords(
#         doc
#     )

#     tagged_tokens = pos_tagger.tag(
#         doc
#     )

#     entities = ner_extractor.extract(doc)

#     dependencies=parser.parse(doc)
    
#     keywords=keyword_extractor.extract(
#         doc
#     )
        

#     analyse=document_analyser.analyse(doc=doc,entities=entities,keywords=keywords)

#     results = tf_idf_extractor.extract(
#         normalised_text
#     )
#     print(results)
#     return {
#         "title": result.title,
#         "cleaned_text": cleaned_text[:3000],
#         "normalized_text": normalised_text[:3000]
#     }

# @app.get("/corpus/tfidf")
# def corpus_tfidf(db: Session = Depends(get_db)):

#     corpus = get_corpus(db)

    
#     extractor = CorpusTFIDFExtractor(
#         corpus=corpus
#     )

#     similarity = DocumentSimilarity(
#         extractor.tfidf_matrix
#     )

#     return (
#     similarity.get_similar_documents(
#         document_index=0
#     )
# )

    
# @app.get("/test/topics")
# def test_topics():

#     sources = [
#         "https://en.wikipedia.org/wiki/Virat_Kohli",
#         "https://en.wikipedia.org/wiki/Sachin_Tendulkar",
#         "https://en.wikipedia.org/wiki/MS_Dhoni",
#         "https://en.wikipedia.org/wiki/FastAPI",
#         "https://en.wikipedia.org/wiki/Django_(web_framework)"
#     ]

#     processor = TextProcessor()

#     documents = []
#     titles = []

#     for source in sources:

#         result = ingest(
#             source_type="web",
#             source=source
#         )

#         cleaned_text = processor.clean_text(
#             result.raw_text
#         )

#         normalised_text = processor.normalize_text(
#             cleaned_text
#         )

#         documents.append(
#             normalised_text
#         )

#         titles.append(
#             result.title
#         )

#     topic_modeller = TopicModeller(
#         num_topics=2,
#         top_n_words=10,
#         max_features=1000
#     )

#     topic_result = topic_modeller.fit_transform(
#         documents=documents,
#         titles=titles
#     )

#     return topic_result    


# @app.get("/test/summary")
# def test_summary():

#     result = ingest(
#         source_type="web",
#         source="https://en.wikipedia.org/wiki/Virat_Kohli"
#     )

#     processor = TextProcessor()

#     cleaned_text = processor.clean_text(
#         result.raw_text
#     )

#     summary_doc = processor.tokenize(
#         cleaned_text
#     )

#     summarizer = ExtractiveSummarizer()

#     summary = summarizer.summarize(
#         doc=summary_doc,
#         max_sentences=5
#     )

#     print("summary", summary)

#     return {
#         "title": result.title,
#         "summary": summary
#     }

# @app.get("/test/nlp-pipeline")
# def test_nlp_pipeline():

#     ingestion_result = ingest(
#         source_type="web",
#         source="https://en.wikipedia.org/wiki/Virat_Kohli"
#     )

#     nlp_service = NLPAnalysisService()

#     result = nlp_service.analyse_document(
#         ingestion_result=ingestion_result,
#         max_summary_sentences=5
#     )

#     return result
####################################


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )