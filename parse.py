import cgi

home_rule_act = open("source_docs/home_rule_act_july2012.txt").read()

home_rule_act = home_rule_act.decode("utf8")
home_rule_act = home_rule_act.replace(u"\u000C", "\n")

front_paragraphs = []
paragraphs = []
back_paragraphs = []

for line in home_rule_act.split("\n"):
	if line.startswith(" "):
		paragraphs.append(line.lstrip())
	else:
		paragraphs[-1] += " " + line

# Extract front matter, through the Table of Contents
main_start = paragraphs.index("TITLE I - SHORT TITLE, "
			      "PURPOSES, AND DEFINITIONS ")	
front_paragraphs = paragraphs[:main_start]
# Extract back matter, which starts with Organic and Amendment History
back_start = paragraphs.index("DISTRICT OF COLUMBIA HOME RULE ACT")
back_paragraphs = paragraphs[back_start:]

# The remainder are main body paragraphs
paragraphs = paragraphs[main_start:back_start]

print paragraphs

# Process main body paragraphs
for p in paragraphs:
	print "<p>" + cgi.escape(p).encode("utf8") + "</p>"
	
