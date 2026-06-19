from spacy.tokens import Doc

class POSTagger:

    def tag(self,doc: Doc):

        results=[]

        for token in doc:

            results.append(
                {
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "tag": token.tag_
                }
            )
        return results    