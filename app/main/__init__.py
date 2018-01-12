#
from .graphData import Neo4j
from .views import app
Neo4j._graph.run("CREATE CONSTRAINT on (n:Pin) ASSERT n.fullName IS UNIQUE")