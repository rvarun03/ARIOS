from collections import Counter
from spacy.tokens import Doc

class ExtractiveSummarizer:
    
    IMPORTANT_POS = {
        "NOUN",
        "PROPN",
        "VERB",
        "ADJ"
    }

    def summarize(
      self,
      doc:Doc,
      max_sentences: int = 5      
    )-> list[dict]:
        
        if doc is None:
            return[]
        
        sentences=list(doc.sents)

        if not sentences:
            return[]
        
        word_frequencies=self.calculate_word_frequencies(
            doc
        )

        if not word_frequencies:
            return[]
        
        sentence_scores=self._score_sentences(
            sentences=sentences,
            word_frequencies=word_frequencies
        )

        top_sentences=self._select_top_sentences(
            sentence_scores=sentence_scores,
            max_sentences=max_sentences
        )
    
        return top_sentences
    
    def _score_sentences(
        
        self,
        sentences:list,
        word_frequencies:Counter
    ):
        sentence_scores=[]

        max_frequency=max(
            word_frequencies.values()
        )

        for sentence_index, sentence in enumerate(sentences):

            score = 0
            important_token_count = 0

            for token in sentence:

                if self.is_important_token(token):
                    
                    lemma=token.lemma_.lower()

                    normalised_frequency=(
                        word_frequencies[lemma]
                        /max_frequency
                    )

                    score+=normalised_frequency
                    important_token_count+=1

            if important_token_count==0:
                continue
            
            final_score=score/important_token_count

            sentence_scores.append(
                {
                    "sentence_index": sentence_index,
                    "sentence": sentence.text.strip(),
                    "score": round(
                        float(final_score),
                        4
                    )
                }
            )
        return sentence_scores

    def calculate_word_frequencies(
            self,
            doc:Doc
        )-> Counter:

        word_frequencies=Counter()

        for token in doc:
            if self.is_important_token(token):
                lemma=token.lemma_.lower()
                word_frequencies[lemma]+=1

        return word_frequencies

    def _select_top_sentences(
        self,
        sentence_scores: list[dict],
        max_sentences: int
    )-> list[dict]:

        top_sentences=sorted(
            sentence_scores,
            key=lambda item: item["score"],
            reverse=True
        )[:max_sentences]

        top_sentences = sorted(
            top_sentences,
            key=lambda item: item["sentence_index"]
        )

        return top_sentences   

    def is_important_token(
            self,
            token
        )-> bool:

        return(
            token.is_alpha
            and not token.is_stop
            and token.pos_ in self.IMPORTANT_POS
        )           
