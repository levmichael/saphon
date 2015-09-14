
# PYTHONPATH must include $SAPHON_ROOT/python.

clean:
	rm -r html

html:
	mkdir html
	python3 ../python/saphon/web/write.py ../data html
	rsync -r intact/* html

publish-hidden: html
	rsync -r html/* saphon@linguistics.berkeley.edu:public_html/hidden/

publish-main: html
	rsync -r html/* saphon@linguistics.berkeley.edu:public_html/
