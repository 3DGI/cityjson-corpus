# stress_relation_graph

## Intent

Synthetic stress case with dense parent/child and object reference relations.

## Why This Shape

Graph-like relations are useful for testing lookup structures and traversal
algorithms. The case should keep geometry small and relationships dense so
resolution work is the limiting factor.

## Performance Signal

This case surfaces:

- relation resolution cost,
- hash lookup pressure,
- traversal cost on dense object graphs,
- allocation behavior for link tables and intermediate maps.

## Recommended Use

Use this to stress hierarchy handling and relation-heavy object models.

