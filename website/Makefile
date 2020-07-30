
# PYTHONPATH must include $SAPHON_ROOT/python.

clean:
	rm -r html

html:
ifdef GOOGLE_MAPS_API_KEY
	mkdir html
	python ../python/saphon/web/write.py ../langs html ../resources/ipa-table.txt
	for lang in en es pt; do \
		sed -i.bak -e "s/{GOOGLE_MAPS_API_KEY}/${GOOGLE_MAPS_API_KEY}/g" intact/$$lang/index.php; \
	done
	rsync -a intact/* html
else
	@echo 1>&2 "The GOOGLE_MAPS_API_KEY environment variable must be set. (If deploying on github, set as a github repo secret.)"
	false
endif

publish-hidden: html
	rsync -a html/* saphon@linguistics.berkeley.edu:public_html/hidden/

publish-main: html
	rsync -a html/* saphon@linguistics.berkeley.edu:public_html/
