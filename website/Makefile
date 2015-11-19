
# PYTHONPATH must include $SAPHON_ROOT/python.

clean:
	rm -r html

html:
	mkdir html
	python3 ../python/saphon/web/write.py ../data html
	rsync -a intact/* html

publish-hidden: html
	rsync -a html/* saphon@linguistics.berkeley.edu:public_html/hidden/

publish-main: html
	rsync -a html/* saphon@linguistics.berkeley.edu:public_html/
