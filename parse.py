import cgi, re

home_rule_act = open("source_docs/home_rule_act_july2012.txt").read()

home_rule_act = home_rule_act.decode("utf8")
home_rule_act = home_rule_act.replace(u"\u000C", "\n")

# incorrect encoding of en-dashes
home_rule_act = re.sub(r" B(\s)", ur" \u2013 \1", home_rule_act)

# incorrect encoding of section symbol
home_rule_act = re.sub(r" Code '", u" Code \xa7", home_rule_act)

front_paragraphs = []
paragraphs = []
back_paragraphs = []

# combine lines into paragraphs
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
# Extract back matter, which starts with Organic and Amendment History
back_start = paragraphs.index("DISTRICT OF COLUMBIA HOME RULE ACT")
back_paragraphs = paragraphs[back_start:]

# The remainder are main body paragraphs
paragraphs = paragraphs[main_start:back_start]

# Process main body paragraphs

# infer with-section list hierarchy

def get_list_level_type(text):
	initial_level_type_res = [
		r'A',
		r'1',
		r'a',
		r'i',
	]
	noninitial_level_type_res = [
		r'[A-Z]+',
		r'[0-9]+[A-Za-z]*',
		r'[a-z]+',
		r'[xvi]+',
	]
	
	initial_levels = set(i for i, r in enumerate(initial_level_type_res) if re.match(r+"$", text))
	noninitial_levels = set(i for i, r in enumerate(noninitial_level_type_res) if re.match(r+"$", text)) - initial_levels
	
	return initial_levels, noninitial_levels
	
list_level_must_follow = {
	(2, 'i'): 'h',
	(2, 'ii'): 'ih',
	(2, 'iii'): 'iih',
}

paragraphs = [
	{ "indent": None,
	  "text": p,
	  "section_num": None,
	  "dc_code_cite": None,
	} for p in paragraphs]

cur_list_style_levels = { }
for p in paragraphs:
	m = re.match(r"(SEC\. \w+\. )?(\[D\.C\. (?:Official )?Code .*?\] )?((?:\(\S+\)\s*)*)", p["text"])
	if not m: continue
		
	section_head, dc_code_cite, paragraph_heads = m.groups()
	
	# starts a new section
	if section_head:
		p["section_num"] = section_head
		p["dc_code_cite"] = dc_code_cite
		cur_list_style_levels = { }

	if paragraph_heads:
		#p['text'] += " " + repr(cur_list_style_levels)
		
		list_levels = re.findall(r"\((.*?)\)", paragraph_heads)
		for i, ll in enumerate(list_levels):
			initial_levels, continued_levels = get_list_level_type(ll)

			# at the start of a section, or immediately inside another list level, we are necessarily starting a level
			original_continued_levels = continued_levels
			if (i == 0 and section_head) or i > 0:
				continued_levels = set()
			
			# See if the continued_levels match any existing level:
			for cl in continued_levels:
				if cl in cur_list_style_levels and ((cl,ll) not in list_level_must_follow or list_level_must_follow[(cl,ll)] == cur_list_style_levels[cl][1]):
					p["indent"] = cur_list_style_levels[cl][0]
					
					# pop any inner levels
					for cl2 in list(cur_list_style_levels):
						if cur_list_style_levels[cl2][0] > cur_list_style_levels[cl][0]:
							del cur_list_style_levels[cl2]
							
					break
					
			else:
				if len(initial_levels) == 0:
					# Fall back.
					initial_levels = original_continued_levels
					
					# No fallback?
					if len(initial_levels) == 0: raise ValueError("Unmatched initial list level: " + repr(ll))
					
				# No continued level matches. Make a new level.
				il = list(initial_levels).pop(0)
				n = (max(v[0] for v in cur_list_style_levels.values()) + 1) if len(cur_list_style_levels) > 0 else 1
				cur_list_style_levels[il] = (n, ll)
				
				# Don't set indentation levels on section paragraphs or if we've already set a level.
				if not section_head and i == 0:
					p["indent"] = n
		
print u"""
<html>
	<head>
		<title>District of Columbia Home Rule Act</title>
		<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>

		<style>
			body {
				font-family: sans-serif;
				font-size: 14px;
				line-height: 19px;
				max-width: 50em;
				padding: 2em;
			}
		</style>
	</head>
	<body>
	
<center>
<h1>District of Columbia Home Rule Act</h1>
<p>(AMENDED THROUGH July 18, 2012)</p>

<p>Public Law 93-198; 87 Stat. 774<br/>
D.C. Official Code \xa7 1-201.01 et seq.<br/>
Approved December 24, 1973</p>


<p>Prepared by</p>
<p>Office of the General Counsel</p>
<p>Council of the District of Columbia</p>
<p>Suite 4</p>
<p>1350 Pennsylvania Street, N.W.</p>
<p>Washington, D.C. 20004</p>
<p>(202) 724-8026</p>


                                         Revised July 23, 2012
       This document depicts the District of Columbia Home Rule Act
    as enacted by the Congress in December, 1973, and amended through
   May 30, 2011, the date of the last congressional amendment before the
printing of this document. The text of the Act is in the original format as en-
  acted and amended. Where the Office of the General Counsel has added
       brief annotations to the text, those annotations appear in brackets.

        Provisions of the District of Columbia Home Rule Act that
     amend other acts are not included in this document except for those
      amendatory provisions found in Title IV (The District Charter).




              This document has been updated for printing on:

                             February 18, 2010
                               July 17, 2009
                             November 3, 2008
                               June 6, 2007
                               April 1, 2005
                                July 7, 2004
                              October 5, 2001
                             January 28, 1999
                             February 24, 1998

                                                          8.18.10
             COUNCIL OF THE DISTRICT OF
                     COLUMBIA


                  Phil Mendelson, Chairman

Yvette M. Alexander                       Jack Evans
Marion Barry                              Jim Graham
Muriel Bowser                             Kenyan McDuffie
Michael A. Brown                          Vincent B. Orange, Sr.
David A. Catania                          Tommy Wells
Mary M. Cheh




          OFFICE OF THE GENERAL COUNSEL

                 Under Whose Direction This
                 Document Has Been Prepared

             V. David Zvenyach, General Counsel
              John Hoellen, Legislative Counsel
            Benjamin Bryant, Codification Counsel
         Katherine Westcott, Assistant General Counsel
          Melissa Tucker, Assistant General Counsel
         Manasi Venkatesh, Assistant General Counsel
            Karen R. Barbour, Legislative Assistant
                   Ada Arrington, Secretary

	
""".encode("utf8")

for p in paragraphs:
	print ("<p style='margin-left: %dem'>" % (p['indent'] if p['indent'] else 0)) + cgi.escape(p["text"]).encode("utf8") + "</p>"
		
print """
	</body>
</html>
"""
