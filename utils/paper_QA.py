import os
from langchain_neo4j import Neo4jVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDGWTFPppWNVJARFTHuaWKVg-ENwCQOuxE"

def paper2doc(papers):
    '''
    papers is a list of papers in json format. 
    Refer to paper_ontology.py for generation process 
    '''
    docs = []
    for p in papers:
        for s in p['sections']:
            doc = Document(page_content=s['section_content'],
                           metadata={'title': p['title'], 'section_title': s['section_title']})
            docs.append(doc)
    return docs


class EmbeddingDB:
    def __init__(self, uri, user, password, docs):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.db = Neo4jVector.from_documents(
            docs, embeddings, url=uri, username=user, password=password
        )

    def insert(self, docs):
        self.db.add_documents(docs)

    def query(self, query, n=2, doPrint=True):
        docs_with_score = self.db.similarity_search_with_score(query, k=n)
        for doc, score in docs_with_score:
            print("-" * 80)
            print("Score: ", score)
            print(doc.page_content)
            print("-" * 80)
        return docs_with_score

'''
import google.generativeai as genai
from google.api_core import retry

genai.configure(api_key='AIzaSyDGWTFPppWNVJARFTHuaWKVg-ENwCQOuxE')
retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
class GeminiEmbeddingFunction:
    # Specify whether to generate embeddings for documents, or queries
    document_mode = True

    def __call__(self, input):
        if self.document_mode:
            embedding_task = "retrieval_document"
        else:
            embedding_task = "retrieval_query"

        retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}

        response = genai.embed_content(
            model="models/text-embedding-004",
            content=input,
            task_type=embedding_task,
            request_options=retry_policy,
        )
        return response["embedding"]
'''