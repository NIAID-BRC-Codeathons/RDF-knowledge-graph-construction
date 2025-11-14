# Triplestore 


## Commands for running Qlever instance

These need to be run from  ./triplestore/BV-BRC

**Do not run get data unless you need to build a new index**
```bash
qlever get-data
```

**Do not run index unless you need to build a new index**
```bash
qlever index --overwrite-existing
```

```bash
qlever start
```

```bash
qlever stop
```

```bash
qlever ui
```


# Visualizations

An example of type to type relation image for the test graph

![graphimage1.png](images/graphimage1.png)

Network showing relation between pathogen and spatial location

![pathogenLocationExample.png](images/pathogenLocationExample.png)

Example of pagerank values for the network of the pathogen to spatial location network

![pagerank.png](images/pagerank.png)