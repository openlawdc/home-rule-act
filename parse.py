import cgi

home_rule_act = open("source_docs/home_rule_act_july2012.txt").read()

home_rule_act = home_rule_act.decode("utf8")
home_rule_act = home_rule_act.replace(u"\u000C", "\n")

front_paragraphs = []
paragraphs = []

for line in home_rule_act.split("\n"):
	if line.startswith(" "):
		paragraphs.append(line.lstrip())
	else:
		paragraphs[-1] += " " + line

# Extract front matter, through the Table of Contents
main_start = paragraphs.index("TITLE I - SHORT TITLE, "
			      "PURPOSES, AND DEFINITIONS ")	
front_paragraphs = paragraphs[:main_start]
paragraphs = paragraphs[main_start:]

# Process main body paragraphs
for p in paragraphs:
	print "<p>" + cgi.escape(p).encode("utf8") + "</p>"
	
