import os
from langchain_neo4j import Neo4jVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document


def paper2doc(papers, tag=None):
    '''
    papers is a list of papers in json format. 
    Refer to paper_ontology.py for generation process 
    '''
    docs = []
    for p in papers:
        for s in p['sections']:
            if tag:
                doc = Document(page_content=s['section_content'],
                           metadata={'title': p['title'], 'section_title': s['section_title'], 'tag': tag})
            else:
                doc = Document(page_content=s['section_content'],
                           metadata={'title': p['title'], 'section_title': s['section_title']})
            docs.append(doc)
    return docs


class EmbeddingDB:
    def __init__(self, uri, user, password, docs):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004") #require api key in os.environ["GOOGLE_API_KEY"]
        self.db = Neo4jVector.from_documents(
            docs, embeddings, url=uri, username=user, password=password
        )

    def insert(self, docs):
        self.db.add_documents(docs)

    def query(self, query, filterdict=None, n=2, doPrint=True):
        # Sample filter: {'tag':'nips2024'}
        if filterdict:
            docs_with_score = self.db.similarity_search_with_score(query, filter=filterdict, k=n)
        else:
            docs_with_score = self.db.similarity_search_with_score(query, k=n)
        for doc, score in docs_with_score:
            print("-" * 80)
            print("Score: ", score)
            print(doc.page_content)
            print("-" * 80)
        return docs_with_score


