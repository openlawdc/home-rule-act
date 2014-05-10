index.xml: front_matter.xml
	python parse.py | xmllint --format - > index.xml 
