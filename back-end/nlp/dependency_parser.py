from spacy.tokens import Doc

class DependencyParser:
    def parse(self,doc:Doc):
        relationships=[]
        for token in doc:
            relationships.append(
                {
                    "text":token.text,
                    "dependency": token.dep_,
                    "head":token.head.text
                }
            )

        return relationships        