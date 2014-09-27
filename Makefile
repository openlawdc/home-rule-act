index.xml: front_matter.xml source_docs/home_rule_act_july2012.txt parse.py
	python parse.py | xmllint --format - > index.xml 
