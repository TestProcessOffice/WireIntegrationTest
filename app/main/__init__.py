#
from .graphData import Neo4j
from .views import app
#Neo4j._graph.run("DROP CONSTRAINT on (n:pin) ASSERT n.fullName IS UNIQUE")
Neo4j._graph.run("CREATE INDEX on :pin(fullName)")
Neo4j._graph.run("CREATE INDEX on :pin(connectorName)")