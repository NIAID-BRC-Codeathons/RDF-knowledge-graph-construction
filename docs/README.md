# README


## Code 

* discuss the code and how it defines the fields in the REST call

## RDF Generation and evolution suggestions

During the codeathon, a simple JSON-LD document was created as a template.  This represents a reference profile for encoding the 
ENA Taxon REST call results.

That document was then used by the code and modified via JSON path expressions to update or prune
nodes based on data values.  This is slow and fragile.
Once a profile is settled on, a function can be developed that will
leverage direct generation of triples.  

Examples that could be used include RDFlib (https://rdflib.readthedocs.io/en/stable/intro_to_creating_rdf.html) PyOxigraph(https://pyoxigraph.readthedocs.io/en/stable) or, recommended, the new Pyjelly (https://github.com/jelly-rdf/pyjelly) package which is focused specifically on large scale data dumps and performant streaming. 

Example in Pyjelly

```python
import pyjelly  # Assuming import; check repo for exact usage

# Hypothetical example; consult docs for API
graph = pyjelly.Graph()
graph.add("https://example.org/person/alice", "https://example.org/name", "Alice")
serialized = graph.serialize("jelly")  # Fast serialization
```

## Future Connections

The decision was made to leverage schema.org and the
associated bioschema.org as the foundation for the profile.

This approach also allows for future alignment with other 
projects, beyond bioschema.org, that are using schema.org as 
a based layer for profiles.  These include:

MLCommons Croissant and GeoCroissant:
* https://mlcommons.org/working-groups/data/croissant/

CODATA Cross Domain Interoperability Framework (CDIF):
https://cross-domain-interoperability-framework.github.io/cdifbook/introduction.html


Earth Science Information Partners (ESIP) Science on Schema.org (SOSO).
https://github.com/ESIPFed/science-on-schema.org/tree/1.3.1



