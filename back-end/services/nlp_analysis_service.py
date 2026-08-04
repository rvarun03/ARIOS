from nlp.text_processor import TextProcessor
from nlp.NER import NER
from nlp.keyword_extractor import KeywordExtractor
from nlp.extractive_summarizer import ExtractiveSummarizer
from nlp.document_analyser import DocumentAnalyzer

class NLPAnalysisService:
    
    """
    Central NLP pipeline service.

    This service takes one ingested document and runs all NLP steps:
    - cleaning
    - normalization
    - tokenization
    - entity extraction
    - keyword extraction
    - summarization
    - document analysis
    """

    def __init__(self):
        
        self.processor=TextProcessor()
        self.ner_extractor = NER()
        self.keyword_extractor = KeywordExtractor()
        self.summarizer = ExtractiveSummarizer()
        self.document_analyzer = DocumentAnalyzer()

    def analyse_document(
        self,
        ingestion_result,
        max_summary_sentences: int = 5
    ) -> dict:
        
        raw_text = ingestion_result.raw_text or ""

        cleaned_text=self.processor.clean_text(
            raw_text
        )

        normalised_text= self.processor.normalize_text(
            cleaned_text
        )

        doc=self.processor.tokenize(
            cleaned_text
        )

        entities= self.ner_extractor.extract(
            doc,
            max_entities=100
        )

        keywords= self.keyword_extractor.extract(
            doc,
            top_n=50
        )

        summary = self.summarizer.summarize(
            doc=doc,
            max_sentences=max_summary_sentences
        )

        analysis = self.document_analyzer.analyse(
            doc=doc,
            keywords=keywords,
            entities=entities,
            summary=summary
        )
        
        return {
            "title": ingestion_result.title,
            "source_type": ingestion_result.source_type,
            "source_url": ingestion_result.source_url,
            "text": {
                "raw_text_length": len(raw_text),
                "cleaned_text_length": len(cleaned_text),
                "normalised_text_length": len(normalised_text),
                "cleaned_text": cleaned_text,
                "preview": cleaned_text[:1000]
            },
            "analysis": analysis
        }
            