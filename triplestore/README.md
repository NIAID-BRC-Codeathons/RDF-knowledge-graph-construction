# Triplestore work around Qlever


## Commands

Do not run get data unless you need to build a new index

```bash
qlever get-data
```

Do not run index unless you need to build a new index
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




## Notes

The structured data graph (sdg) and the lexical graph (lg) 
will connect on run_accession.  