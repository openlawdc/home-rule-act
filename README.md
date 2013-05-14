# home-rule-act

Nicely format the DC Home Rule Act, which is DC's constitution.

Requires Python to build.

To regenerate, run

    make

## architecture

`index.html` is the end-product, and is built by parsing `source_docs/home_rule_act_july2012.txt`
with `parse.py`, concatenating `front_matter.html` onto generated HTML.
