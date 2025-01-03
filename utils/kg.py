# pip install neo4j
#from neo4j import GraphDatabase
## start new neo4j instance 
# docker run \
#   -p7474:7474 \                       # forward port 7474 (HTTP)
#   -p7687:7687 \                       # forward port 7687 (Bolt)
#   -d \                                # run in background
#   -e NEO4J_AUTH=neo4j/secretgraph \   # set login credentials
#   neo4j:latest
#https://neo4j.com/docs/python-manual/current/install/
#URI = "neo4j://localhost:7687"
#AUTH = ("neo4j", "secretgraph")
#self.driver = GraphDatabase.driver(uri, auth=(user, password))