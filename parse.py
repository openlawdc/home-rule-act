import cgi, re

home_rule_act = open("source_docs/home_rule_act_july2012.txt").read()

home_rule_act = home_rule_act.decode("utf8")

# recode page numbering
#home_rule_act = re.sub(u"(\d+)\n(\u000C)", u"\n [\u000C]\n ", home_rule_act) # brackets prevent para collapse
home_rule_act = re.sub(u"(\d+)\n(\u000C)", u"\n\n", home_rule_act) # we don't care about pages, this is a bad character

# incorrect encoding of en-dashes
home_rule_act = re.sub(r" B(\s)", ur" \u2013 \1", home_rule_act)

# incorrect encoding of section symbol
home_rule_act = re.sub(r" Code '", u" Code \xa7", home_rule_act)

# combine lines into paragraphs
paragraphs = []
for line in home_rule_act.split("\n"):
	if len(paragraphs) > 0 and re.search(r"\w", line) and re.search(r"\w", paragraphs[-1]) and line == line.upper() and paragraphs[-1] == paragraphs[-1].upper():
		# Collapse two all-caps lines in a row.
		paragraphs[-1] += " " + line.strip()
	elif line.startswith(" ") or line.strip() == "":
		paragraphs.append(line.lstrip())
	else:
		paragraphs[-1] += " " + line

# Extract front matter, through the Table of Contents
main_start = paragraphs.index('TITLE I - SHORT TITLE, PURPOSES, AND DEFINITIONS')
front_paragraphs = paragraphs[:main_start]
# Extract back matter, which starts with Organic and Amendment History
back_start = paragraphs.index("DISTRICT OF COLUMBIA HOME RULE ACT ORGANIC AND AMENDATORY HISTORY")
back_paragraphs = paragraphs[back_start:]
# The remainder are main body paragraphs
paragraphs = paragraphs[main_start:back_start]

# Process main body paragraphs

unparsed_paragraphs = [
	{ "indent": 0,
	  "text": p.strip(),
	} for p in paragraphs if p.strip() != ""]

paragraphs = []
for p in unparsed_paragraphs:
	paragraphs.append(p)

	m = re.match(r"(SEC\. \w+\.? )?(\[D\.C\. (?:Official )?Code [^\]]*\]\.? )?((?:\(\S+\)\s*)*)(?:(.*\S) --\s*)?", p["text"], re.I)

	m_heading = re.match(r"(?:(TITLE|PART|Subpart)\ ([\w\-]+))\s[\s\-]*(.*)", p["text"])
	try:
		p["heading-type"] = m_heading.group(1).lower()
		p["num"] = m_heading.group(2)
		p["heading"] = m_heading.group(3)
		continue
	except AttributeError:
		pass

	section_num, dc_code_cite, paragraph_heads, heading = m.groups()

	# chop off the section head and citation info
	p["text"] = p["text"][len(m.group(0)):]

	# starts a new section
	if section_num:
		p["heading-type"] = "section"
		p["num"] = re.sub(r"(SEC|Sec)\. (.*\S)\.", ur"\2", section_num).strip()
		if not paragraphs[-2].get("heading-type"):
			p["heading"] = paragraphs.pop(-2)["text"]
		p["dc_code_cite"] = dc_code_cite
		if heading: # not sure what this text really is
			paragraphs.append({ "indent": 0, "text": heading })
		continue

	if paragraph_heads:
		p["para_num"] = paragraph_heads
		p["heading"] = heading

# Compute indentation levels within each section.
def assign_indentation(section_paragraphs):
	# Get a flat list of symbols.
	para_symbols = []
	for p in section_paragraphs:
		if p.get("para_num"):
			list_levels = re.findall(r"\((.*?)\)", p["para_num"])
			para_symbols.extend(list_levels)

	if len(para_symbols) == 0: return

	# Solve indentation level.
	from infer_list_indentation import infer_list_indentation
	indents = infer_list_indentation(para_symbols)
	if indents == None: return # could not figure it out

	# Apply.
	for p in section_paragraphs:
		if p.get("para_num"):
			if p.get("heading-type") != "section": p["indent"] = indents[0][0]+1
			list_levels = re.findall(r"\((.*?)\)", p["para_num"])
			for ll in list_levels: indents.pop(0)

cur_section = []
for p in paragraphs:
	if p.get("heading-type") == "section":
		if len(cur_section) > 0: assign_indentation(cur_section)
		cur_section = []
	cur_section.append(p)
if len(cur_section) > 0: assign_indentation(cur_section)

print open("front_matter.xml").read()

level_types = ('title', 'part', 'subpart', 'section')
big_stack = []
little_stack = 0

for p in paragraphs:
	if p["text"] == u"[\u000C]":
		#print "<hr>"
		continue

	#if "ref" in p:
	#	ref = "--".join(p["ref"])
	#	ref = cgi.escape(ref).encode("utf8")
	#	print "<a name='" + ref + "'> </a>"

	if p.get("heading-type"):
		while little_stack > 0:
			print "</level>"
			little_stack -= 1

		while big_stack and level_types.index(big_stack[-1]) >= level_types.index(p["heading-type"]):
			print "</level>"
			big_stack.pop()

		big_stack.append(p["heading-type"])

		print """
<level type="toc">
	<prefix>%s</prefix>
	<num>%s</num>
""" % (p["heading-type"].title(), cgi.escape(p["num"]).encode("utf8"))

		if p.get("dc_code_cite"): print "\t<dc-code-parallel-citation>%s</dc-code-parallel-citation>" % cgi.escape(p["dc_code_cite"]).encode("utf8")
		if p.get("heading"): print "\t<heading>%s</heading>" % cgi.escape(p["heading"]).encode("utf8")
		if p.get("text"): print "\t<text>%s</text>" % cgi.escape(p["text"]).encode("utf8")

	else:

		if p.get("para_num") or p.get("heading"):
			while little_stack >= p['indent']:
				print "</level>"
				little_stack -= 1
			little_stack += 1

			print "<level>"
			if p.get("para_num"): print "\t<num>%s</num>" % cgi.escape(p["para_num"]).encode("utf8").strip()
			if p.get("heading"): print "\t<heading>%s</heading>" % cgi.escape(p["heading"]).encode("utf8")
			print "<text>%s</text>" % cgi.escape(p["text"]).encode("utf8")

		else:
			if p["text"].strip() == "": continue

			print """
<text>%s</text>
""" % cgi.escape(p["text"]).encode("utf8")

while little_stack > 0:
	print "</level>"
	little_stack -= 1

while big_stack:
	print "</level>"
	big_stack.pop()

print """
</level>
"""
