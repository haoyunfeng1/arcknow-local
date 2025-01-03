#pip install gTTS
from neo4j import GraphDatabase
import google.generativeai as genai
import json 
from gtts import gTTS
from pathlib import Path
from utils.icml_parser import paper_json_to_text

class PaperOntology:
    def __init__(self, 
                 paper,
                 flash):
        '''
        paper is in string format. Parsed from pdf. 
        '''
        self.paper = paper
        self.flash = flash
        self.ontology = None
        self.summary = None

    def create_ontology_json(self):
        response = self.flash.generate_content(
            '''
            You are an IR researcher tasks with extracting information from papers 
            and structuring it in a property graph to inform further research Q&A.
            
            Extract the entities (nodes) and specify their type from the following Input text.
            Also extract the relationships between these nodes. the relationship direction goes from the start node to the end node. 
            
            Return result as JSON using the following format:
            {{"nodes": [ {{"id": "0", "properties": {{"label": "the type of entity", "name": "name of entity" }} }}],
              "relationships": [{{start": "0", "end": "1", "properties": {{"label": "TYPE_OF_RELATIONSHIP", "details": "Description of the relationship"}} }}] }}
            
            - Use only the information from the Input text. Do not add any additional information.  
            - If the input text is empty, return empty Json. 
            - Make sure to create as many nodes and relationships as needed to offer rich medical context for further research.
            - An AI knowledge assistant must be able to read this graph and immediately understand the context to inform detailed research questions. 
            - Multiple documents will be ingested from different sources and we are using this property graph to connect information, so make sure entity types are fairly general. 
            
            Use only fhe following nodes and relationships (if provided):
            {schema}
            
            Assign a unique ID (string) to each node, and reuse it to define relationships.
            Do respect the source and target node types for relationship and
            the relationship direction.
            
            Do not return any additional information other than the JSON in it.

            Input text:
            
            ''' + paper_json_to_text(self.paper)
        )
        for s,c in enumerate(response.text):
            if c == '{':
                break
        for e in range(len(response.text)-1, -1, -1):
            if response.text[e] == '}':
                break
        paper_ontology = json.loads(response.text[s:e+1])
        self.ontology = paper_ontology
        return paper_ontology

    def create_summary(self):
        response = self.flash.generate_content(
            '''
            You are a researcher in information retrieval area. You want to give an overview of a paper from a conference. \
            You are giving the overview to business stakeholders who does not have computer science background. \
            You want to inform business why this paper is informative to their business. \
            In the overview, answer the following questions. Make sure your overview can be understood by business stakeholders: \
            - What is the problem statement.
            - What use cases can be impacted
            - Describe the proposed the approach. How is it different from other existing approach?
            - What foundamental techniques is the proposed approach based of?
            - What existing methods, algorithms, or frameworks does the proposed approach use?
            - What benchmarks were tested in experiement? What metrics are reported?
            - What are the other methods does the proposed method outperform?
            - What is the main conclusion of the paper? How does it impact future research and business?
            Paper:
            ''' + paper_json_to_text(self.paper)
        )
        self.summary = response.text 
        return(response.text)

def create_overview(summaries, flash):
    '''
    summaries is a list of paper level summary in string
    '''
    response = flash.generate_content(
        '''
        You are a researcher in information retrieval area. \
        You want to give an overview of all papers published on 2024 conference. \
        The audiences of this overview are 5th graders and you want to get them interested in the domain. \
        In the first section, talk about major use cases discussed in conference papers. \
        In the second section, talk about what problems are being solved by the papers. \
        In the third section, talk about how are the problems being solved. What methods did the authors use. \
        In the fourth section, talk about future research directions. \ 
        Here is the list of overviews of papers in 2024 
        ''' + str(summaries)
    )
    return response.text 

def create_mp3(summary, output_path):
    '''
    The summary is a string of initivial paper summary or all papers overview 
    '''
    myobj = gTTS(text=summary, lang=language, slow=False)
    myobj.save(Path(output_path))
    return 0 

# pip install neo4j
#from neo4j import GraphDatabase
## start new neo4j instance 
# docker run \
#   -p7474:7474 \                       # forward port 7474 (HTTP)
#   -p7687:7687 \                       # forward port 7687 (Bolt)
#   -d \                                # run in background
#   -e NEO4J_AUTH=neo4j/secretgraph \   # set login credentials
#   neo4j:latest
class OntologyKG:
    def __init__(self, uri, user, password):
        #URI = "neo4j://localhost:7687"
        #AUTH = ("neo4j", "secretgraph")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def clean(self):
        self.driver.execute_query('match (a) -[r] -> () delete a, r')
        self.driver.execute_query('match (a) delete a')

    def _node_label(self, name):
        return name.replace(" ", "_")

    def _node_query(self, node):
        q = f'MERGE (a:{self._node_label(node['properties']['label'])} {{ name:"{node["properties"]["name"]}" }}) \
        ON CREATE set a.test="test"' 
        return q

    def _rel_query(self, nodes, rel):
        q = f'MATCH (s:{self._node_label(nodes[int(rel["start"])]["properties"]["label"])}), \
        (e:{self._node_label(nodes[int(rel["end"])]["properties"]["label"])}) \
        WHERE s.name="{nodes[int(rel["start"])]["properties"]["name"]}" AND \
        e.name="{nodes[int(rel["end"])]["properties"]["name"]}" \
        CREATE (s)-[rel:{rel["properties"]["label"]}]->(e)'
        return q

    def insert(self, ontology_json):
        for n in ontology_json["nodes"]:
            self.driver.execute_query(self._node_query(n))
        for rel in ontology_json["relationships"]:
            self.driver.execute_query(self._rel_query(ontology_json["nodes"], rel))
        return 0
        
    