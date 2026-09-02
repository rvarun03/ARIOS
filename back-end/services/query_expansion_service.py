import json
import re

from services.llm_service import LLM_Service

class QueryExpansionService:
    """
    Uses an LLM to rewrite the user's question into better search queries.

    This is used before retrieval.
    It should NOT answer the user's question.
    It only creates search queries.
    """

    def __init__(self):
        self.llm_service = LLM_Service()

    def generate_search_queries(
        self,
        question:str,
        max_queries: int = 4
    ) -> list[str]:

        if not question or not question.strip():
            return []

        prompt= self.__build_prompt(
            question=question,
            max_queries=max_queries
        )

        llm_response = self.llm_service.generate_answer(
            prompt=prompt
        )

        queries = self.__parse_queries_from_response(
            response=llm_response
        )

        queries = self._clean_queries(
            queries=queries,
            original_question=question,
            max_queries=max_queries
        )

        return queries

    def __build_prompt(
        self,    
        question:str,
        max_queries:int
    )-> str:

        return f"""

    You are a query expansion assistant for a RAG search system.

    Your task:
    Rewrite the user's question into search queries that can retrieve the most relevant document chunks.

    Rules:
    1. Do not answer the question.
    2. Do not add factual answers.
    3. Generate only search queries.
    4. Keep the original entity names.
    5. Add related search wording only when it helps retrieval.
    6. Return only valid JSON.
    7. The JSON must be a list of strings.
    8. Generate at most {max_queries} queries.

    User question:
    {question}

    Return format example:
    [
    "original search query",
    "alternative search query",
    "specific factual search query"
    ]
    """

    def __parse_queries_from_response(
        self,
        response:str
    )-> list[str]:

        if not response:
            return []

        response= response.strip()

        try:
            parsed_response=json.loads(response)

            if isinstance(parsed_response,list):
                return[
                    item
                    for item in parsed_response
                    if isinstance(item,str)
                ]

        except json.JSONDecodeError:
            pass

        json_list_match = re.search(
            r"\[[\s\S]*\]",
            response
        )

        if json_list_match:
            try:
                parsed_response = json.loads(
                    json_list_match.group(0)
                )

                if isinstance(parsed_response, list):
                    return [
                        item
                        for item in parsed_response
                        if isinstance(item, str)
                    ]

            except json.JSONDecodeError:
                pass

        return []

    def _clean_queries(
        self,
        queries: list[str],
        original_question: str,
        max_queries: int
    ) -> list[str]:

        cleaned_queries = []

        cleaned_queries.append(
            original_question.strip()
        )

        for query in queries:
            cleaned_query = " ".join(
                query.strip().split()
            )

            if not cleaned_query:
                continue

            cleaned_queries.append(cleaned_query)

        cleaned_queries = self._remove_duplicates(
            cleaned_queries
        )

        return cleaned_queries[:max_queries]

    def _remove_duplicates(
        self,
        items: list[str]
    ) -> list[str]:

        unique_items = []
        seen_items = set()

        for item in items:
            item_key = item.lower()

            if item_key not in seen_items:
                unique_items.append(item)
                seen_items.add(item_key)

        return unique_items

       
