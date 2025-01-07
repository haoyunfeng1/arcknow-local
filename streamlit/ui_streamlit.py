import streamlit as st

def intro():
    import streamlit as st
    st.markdown("# Welcome to Arcknow")

def sigir_demo():
    import streamlit as st
    import pickle
    import google.generativeai as genai
    from google.api_core import retry
    import numpy as np

    genai.configure(api_key="AIzaSyDGWTFPppWNVJARFTHuaWKVg-ENwCQOuxE")
    flash = genai.GenerativeModel('gemini-1.5-flash')
    embedding_task = "retrieval_query"
    retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
    

    tab1, tab2 = st.tabs(["Overviews", "Question Answer"])

    with open("./streamlit_data.pkl", "rb") as f:
        track2paper, overview, metadata, best_paper_scaling, best_paper_workbench, best_paper_short, emb_array_a = pickle.load(f)
        
    with tab1:
        st.markdown("# SIGIR 2024 for Everyone")
        st.markdown("## Overview and Best Papers")
        expander_1 = st.expander("Overview (with audio)")
        expander_1.audio("./welcome.mp3", format="audio/mpeg", loop=True)
        expander_1.markdown(overview)
    
        expander_2 = st.expander("Best paper: Scaling Laws For Dense Retrieval (with audio)")
        expander_2.audio("./best_paper.mp3", format="audio/mpeg", loop=True)
        expander_2.markdown(str(best_paper_scaling))
    
        expander_3 = st.expander("Best paper: A Workbench for Autograding Retrieve/Generate Systems (with audio)")
        expander_3.audio("./best_paper_2.mp3", format="audio/mpeg", loop=True)
        expander_3.markdown(str(best_paper_workbench))
    
        expander_3 = st.expander("Best short paper: Evaluating Retrieval Quality in Retrieval-Augmented Generation (with audio)")
        expander_3.audio("./best_paper_short.mp3", format="audio/mpeg", loop=True)
        expander_3.markdown(str(best_paper_short))
    
        st.markdown("## All Papers")
        for t in track2paper:
            st.markdown("### " + t)
            for title, summary in track2paper[t]:
                expander_i = st.expander(title.strip())
                expander_i.markdown(summary)

    with tab2:
        query = st.text_input("Enter your question about SIGIR 2024")
        if query:
            qemb = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type=embedding_task,
                request_options=retry_policy,
            )
            x = np.dot(qemb["embedding"], emb_array_a)
            docIDs = np.argsort(x)[len(x)-1:-6:-1]
            context = ""
            for i in docIDs:
                context += metadata[i]["doc"] + "\n"
            prompt = f'Answer question based on given context. Question: {query} \n Context: {context}'
            response = flash.generate_content(prompt)
            st.markdown(response.text)
            url = "https://dl.acm.org/doi/proceedings/10.1145/3626772"
            st.markdown("### [References](%s)" % url)
            for i in docIDs:
                st.markdown("[" + metadata[i]["track"] + "] :blue[*" + metadata[i]["title"] + "*]")
                st.markdown(metadata[i]["section_name"])

def icml_demo():
    import streamlit as st
    import pickle
    import google.generativeai as genai
    import os
    from langchain_neo4j import Neo4jVector
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = "AIzaSyDGWTFPppWNVJARFTHuaWKVg-ENwCQOuxE"

    genai.configure(api_key="AIzaSyDGWTFPppWNVJARFTHuaWKVg-ENwCQOuxE")
    flash = genai.GenerativeModel('gemini-1.5-flash')
    
    NEO4J_URI='neo4j+s://e0a3a179.databases.neo4j.io'
    NEO4J_USERNAME='neo4j'
    NEO4J_PASSWORD='D28gPFcuImX_3SQeOHRsVYeZjfmv38iVK7R-jAOZodM'

    tab1, tab2 = st.tabs(["Overviews", "Question Answer"])

    with open("./streamlit_icml_data.pkl", "rb") as f:
        summaries, overview, best_paper_ids, titles = pickle.load(f)

    with tab1:
        st.markdown("# ICML 2024 for Everyone")
        st.markdown("## Overview")
        expander_1 = st.expander("Overview (with audio)")
        expander_1.audio("./overview_icml.mp3", format="audio/mpeg", loop=True)
        expander_1.markdown(overview)

        st.markdown("## Best Papers")
        for i in best_paper_ids['Best Paper']:
            expander = st.expander(titles[i].strip())
            expander.markdown(summaries[i])
        
        #st.markdown("## All Papers")
        #for i, s in enumerate(summaries):
        #    expander = st.expander(titles[i].strip())
        #    expander.markdown(s)

    with tab2:
        query = st.text_input("Enter your question about SIGIR 2024")
        if query:
            index_name = "vector"  # default index name
            embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
            
            store = Neo4jVector.from_existing_index(
                embeddings,
                url=NEO4J_URI,
                username=NEO4J_USERNAME,
                password=NEO4J_PASSWORD,
                index_name=index_name,
            )
            docs = store.similarity_search_with_score(query, k=5)
            context = ''
            meatadata = []
            for doc, score in docs:
                context += doc.page_content + '\n'
                meatadata.append(doc.metadata)
            
            prompt = f'Answer question based on given context. Question: {query} \n Context: {context}'
            response = flash.generate_content(prompt)
            st.markdown(response.text)
            url = "https://dl.acm.org/doi/proceedings/10.1145/3626772"
            st.markdown("### [References](%s)" % url)

            for m in meatadata:
                st.markdown(":blue[*" + m["title"] + "*]")
                st.markdown(m["section_title"])
            

page_names_to_funcs = {
    "—": intro,
    "SIGIR": sigir_demo,
    'ICML': icml_demo
}

st.sidebar.markdown("# Arckdown")
demo_name = st.sidebar.selectbox("Choose a conference", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
        

    





