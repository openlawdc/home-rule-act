import cgi, re

home_rule_act = open("source_docs/home_rule_act_july2012.txt").read()

home_rule_act = home_rule_act.decode("utf8")

# recode page numbering
home_rule_act = re.sub(u"(\d+)\n(\u000C)", u"\n [\u000C]\n ", home_rule_act) # brackets prevent para collapse

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

paragraphs = [
	{ "indent": 0,
	  "text": p,
	  "section_num": None,
	  "dc_code_cite": None,
	  "para_num": None,
	  "title_num": None,
	  "part_num": None,
	  "subpart_num": None
	} for p in paragraphs]

super_structure = { }
for p in paragraphs:
	m = re.match(r"(SEC\. \w+\.? )?(\[D\.C\. (?:Official )?Code [^\]]*\]\.? )?((?:\(\S+\)\s*)*)", p["text"], re.I)

	m_title = re.match(r"(TITLE\ \w+).*", p["text"])
	try:
		p["title_num"] = m_title.groups()[0]
		super_structure["title"] = p["title_num"]
		p["ref"] = (super_structure["title"],)
	except AttributeError:
		pass

	m_part = re.match(r"(PART\ \w+).*", p["text"])
	try:
		p["part_num"] = m_part.groups()[0]
		super_structure["part"] = p["part_num"]
		p["ref"] = (super_structure["title"], super_structure["part"])
	except AttributeError:
		pass

	m_subpart = re.match(r"(Subpart\ \w+).*", p["text"])
	try:
		p["subpart_num"] = m_subpart.groups()[0]
		p["ref"] = (super_structure["title"], super_structure["part"], p["subpart_num"])
	except AttributeError:
		pass

	section_head, dc_code_cite, paragraph_heads = m.groups()

	# chop off the section head and citation info
	p["text"] = p["text"][len(m.group(0)):]

	# starts a new section
	if section_head:
		p["section_num"] = section_head
		p["dc_code_cite"] = dc_code_cite

	if paragraph_heads:
		p["para_num"] = paragraph_heads

# Compute indentation levels within each section.
def assign_indentation(section_paragraphs):
	# Get a flat list of symbols.
	para_symbols = []
	for p in section_paragraphs:
		if p["para_num"]:
			list_levels = re.findall(r"\((.*?)\)", p["para_num"])
			para_symbols.extend(list_levels)

	if len(para_symbols) == 0: return

	# Solve indentation level.
	from infer_list_indentation import infer_list_indentation
	indents = infer_list_indentation(para_symbols)
	if indents == None: return # could not figure it out

	# Apply.
	for p in section_paragraphs:
		if p["para_num"]:
			if not p["section_num"]: p["indent"] = indents[0][0]+1
			list_levels = re.findall(r"\((.*?)\)", p["para_num"])
			for ll in list_levels: indents.pop(0)

cur_section = []
for p in paragraphs:
	if p["section_num"]:
		if len(cur_section) > 0: assign_indentation(cur_section)
		cur_section = []
	cur_section.append(p)
if len(cur_section) > 0: assign_indentation(cur_section)

print open("front_matter.html").read()

print "<h2>Table of Contents</h2>"
print "<div id='toc'>"
for p in paragraphs:
	if "ref" in p:
		ref = "--".join(p["ref"])
		ref = cgi.escape(ref).encode("utf8")

		if p["title_num"]:
			indent = 0
		elif p["part_num"]:
			indent = 1
		elif p["subpart_num"]:
			indent = 2

		print ("<p style='margin-left: %dem'><a href='#" % indent) + ref + "'>" + cgi.escape(p["text"]).encode("utf8") + "</a></a>"

print "</div>"

print "<hr>"

for p in paragraphs:
	if p["text"] == u"[\u000C]":
		print "<hr>"
		continue

	if "ref" in p:
		ref = "--".join(p["ref"])
		ref = cgi.escape(ref).encode("utf8")
		print "<a name='" + ref + "'> </a>"

	if p["title_num"]:
		print "<h2>" + cgi.escape(p["text"]).encode("utf8") + "</h2>"
	elif p["part_num"]:
		print "<h3>" + cgi.escape(p["text"]).encode("utf8") + "</h3>"
	elif p["subpart_num"]:
		print "<h4>" + cgi.escape(p["text"]).encode("utf8") + "</h4>"
	else:
		print ("<p style='margin-left: %dem'>" % (p['indent'] if p['indent'] else 0))
		if p["section_num"]: print "<strong>" + cgi.escape(p["section_num"]).encode("utf8") + "</strong>"
		if p["dc_code_cite"]: print "<small>" + cgi.escape(p["dc_code_cite"]).encode("utf8") + "</small>"
		if p["para_num"]: print "<strong>" + cgi.escape(p["para_num"]).encode("utf8") + "</strong>"
		print cgi.escape(p["text"]).encode("utf8")
		print "</p>"

print """
            </div>
        </div>
	</body>
</html>
"""
