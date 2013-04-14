import cgi

home_rule_act = open("source_docs/home_rule_act_july2012.txt").read()

home_rule_act = home_rule_act.decode("utf8")
home_rule_act = home_rule_act.replace(u"\u000C", "\n")

paragraphs = []

for line in home_rule_act.split("\n"):
	if line.startswith(" "):
		paragraphs.append(line.lstrip())
	else:
		paragraphs[-1] += " " + line
		
for p in paragraphs:
	print "<p>" + cgi.escape(p).encode("utf8") + "</p>"
	
