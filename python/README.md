
To create static html files:

```
cd SAPHON_ROOT/python
mkdir ../html
python3 saphon/web/write.py ../data ../html
```

To publish them:

```
rsync -r ../html/* saphon@linguistics.berkeley.edu:public_html/
```
