# home-rule-act

Nicely format the DC Home Rule Act, which is DC's constitution.

Requires Python to build.

To regenerate the XML, run

    make

To regenerate the HTML, change to the `simple-generator` directory and run:

	node make_index.js ../home-rule-act
	node index.js ../home-rule-act ../home-rule-act/ /home-rule-act ../home-rule-act/index.xml

## architecture

`index.html` is the end-product, and is built by parsing `source_docs/home_rule_act_july2012.txt`
with `parse.py`, concatenating `front_matter.html` onto generated HTML.
