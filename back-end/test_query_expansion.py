from services.query_expansion_service import QueryExpansionService


query_expansion_service = QueryExpansionService()

question = "Who are Virat Kohli's parents?"

queries = query_expansion_service.generate_search_queries(
    question=question
)

print(queries)