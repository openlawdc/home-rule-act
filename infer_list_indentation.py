# Convert a flat sequence of numbered list labels, such as 1 2 a b 3 4,
# into a hierarchical structure:
#
#   1
#   2
#     a
#     b
#   3
#   4
#
# This is particularly hard because roman numeral symbols can be
# interpreted in multiple ways. We solve the problem using
# linear programming to minimize the number of times an invalid
# pair of consecutive symbols occurs, e.g. 'i' should follow 'h'
# if it is a letter-symbol.

import re

def alpha_continue_test(a, b):
	return ord(a[-1]) == ord(b[-1])-1

def infer_list_indentation(
	symbol_list,
	
	initial_symbols=[
		'A',
		'1',
		'a',
		'i',
		'I',
	],
	
	symbol_classes = [
		r'[A-Z]+',
		r'[0-9]+[A-Za-z]*',
		r'[a-z]+',
		r'[xvil]+',
		r'[XVIL]+',
	],
	
	continuation_tests = [
		alpha_continue_test,
		None,
		alpha_continue_test,
		None,
		None,
	],
	
	is_initial=True,
	parent_symbol_class=None,
	memo_table=None,
	
	):

	# Solve this problem by linear programming.
	
	base_score = 0
	
	if is_initial:
		# The first symbol should be an initial symbol and not of the same
		# symbol class as the parent level.
		if symbol_list[0] in initial_symbols:
			level_class = initial_symbols.index(symbol_list[0])
			if level_class == parent_symbol_class: return None
		else:
			# If not, try the first matching symbol class but assign a high score.
			for i, reg in enumerate(symbol_classes):
				if re.match(reg+"$", symbol_list[0]) and i != parent_symbol_class:
					level_class = i
					base_score = 10
					break
			else:
				return None
	else:
		# The first symbol is assumed to be in the parent_symbol_class.
		level_class = parent_symbol_class
		
	# Base cases.

	if len(symbol_list) == 1:
		if parent_symbol_class == None:
			# Top-level call from user.
			return [(0, level_class, symbol_list[0])]
		else:
			# Recursive call.
			return (0, 2, 2, level_class, None, None)
			
	if symbol_list == []: raise ValueError()

	# Get from memo table?
	if memo_table == None: memo_table = { }
	call_args = (tuple(symbol_list), is_initial, parent_symbol_class)
	if call_args in memo_table: return memo_table[call_args]

	# For every possible pair of points where we indent a level and
	# then later "outdent", compute a score. Return the analysis that
	# has the lowest score (least violations).
	solution = None
	for in_pt in xrange(1, len(symbol_list)+2):
		for out_pt in xrange(in_pt+1, len(symbol_list)+3):
			# The symbol at out_pt must match the symbol type.
			if out_pt < len(symbol_list) and not re.match(symbol_classes[level_class]+"$", symbol_list[out_pt]):
				continue
			
			# Score this.
			score = base_score
			
			# From 0 to in_pt, and then the symbol at out_pt, should make
			# a continuous sequence. Add 1 to the score for each invalid
			# pair of consecutive symbols.
			level_symbols = symbol_list[:in_pt] + symbol_list[out_pt:out_pt+1]
			cont_test = continuation_tests[level_class]
			if cont_test:
				for i in xrange(1, len(level_symbols)):
					if not cont_test(level_symbols[i-1], level_symbols[i]):
						score += 1
					
			# Everything from in_pt to out_pt-1 can be scored recursively.
			if in_pt < len(symbol_list):
				inner_solution1 = infer_list_indentation(symbol_list[in_pt:out_pt], initial_symbols=initial_symbols, symbol_classes=symbol_classes, continuation_tests=continuation_tests, is_initial=True, parent_symbol_class=level_class, memo_table=memo_table)
				if inner_solution1 == None: continue # no solution
				score += inner_solution1[0]
			else:
				inner_solution1 = None
			
			# And now recursively score the part from out_pt and on.
			if out_pt < len(symbol_list):
				inner_solution2 = infer_list_indentation(symbol_list[out_pt:], initial_symbols=initial_symbols, symbol_classes=symbol_classes, continuation_tests=continuation_tests, is_initial=False, parent_symbol_class=level_class, memo_table=memo_table)
				if inner_solution2 == None: continue # no solution
				score += inner_solution2[0]
			else:
				inner_solution2 = None
			
			if not solution or score < solution[0]:
				solution = (score, in_pt, out_pt, level_class, inner_solution1, inner_solution2)
				
		# End out_pt loop.
		
		# If this symbol does not match the symbol type, break, because
		# no further point could continue this list.
		if in_pt < len(symbol_list) and not re.match(symbol_classes[level_class]+"$", symbol_list[in_pt]):
			break
		
	# Store in memo table.
	memo_table[call_args] = solution
	
	if parent_symbol_class == None:
		# Top-level call from user.
		if not solution: return None
		def build_solution(symbols, solution, indent):
			ret = [(indent, solution[3], s) for s in symbols[0:solution[1]]]
			if solution[4]: ret += build_solution(symbols[solution[1]:solution[2]], solution[4], indent+1)
			if solution[5]: ret += build_solution(symbols[solution[2]:], solution[5], indent)
			return ret
		return build_solution(symbol_list, solution, 0)
	else:
		# Recursive call.
		return solution
	
	
if __name__ == "__main__":
	ret = infer_list_indentation(['a', '1', '2', 'A', 'B', 'C', 'D', '3', 'A', 'B', 'C', 'D', 'E', 'F', '4', '5', '6', 'b', '1', 'A', 'B', 'i', 'ii', 'iii', 'iv', '2', 'A', 'B', 'C', 'D', 'E', 'c', '1', '2', 'd', '1', '2', '3', '4', '5', 'A', 'B', '6', '7', 'A', 'B', 'C', 'D', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', 'A', 'B', 'C', 'e', '1', 'A', 'B', 'C', 'D', 'i', 'ii', 'iii', 'iv', 'v', 'I', 'II', 'III', 'E', 'i', 'ii', 'iii', 'iv', 'v', '2', 'f', '1', '2', '3'])
	
	for indent, symbol_type, symbol in ret:
		print "  "*indent + symbol, " (type=%d)" % symbol_type
