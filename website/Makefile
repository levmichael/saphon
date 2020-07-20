
# PYTHONPATH must include $SAPHON_ROOT/python.

clean:
	rm -r html

html:
	mkdir html
	python ../python/saphon/web/write.py ../langs html ../resources/ipa-table.txt
	rsync -a intact/* html

publish-hidden: html
	rsync -a html/* saphon@linguistics.berkeley.edu:public_html/hidden/

publish-main: html
	rsync -a html/* saphon@linguistics.berkeley.edu:public_html/
