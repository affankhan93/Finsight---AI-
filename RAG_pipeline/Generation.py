from RAG_pipeline.Retrieval import qa_chain 
from RAG_pipeline.Guardrails import check_input, check_output

chain = qa_chain()

user_query = input("Enter you query here...")

ok, query = check_input(user_query)
if not ok:
    print(query)
    raise SystemExit

response = chain.invoke({'query': user_query})
print("Answer:- ", check_output(response['result']))
print("Source Documents:- ", response['source_documents'])


