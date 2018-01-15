#
from .graphData import Neo4j
from .views import app
Neo4j._graph.run("CREATE CONSTRAINT on (n:pin) ASSERT n.fullName IS UNIQUE")
Neo4j._graph.run("CREATE INDEX on :pin(connectorName)")