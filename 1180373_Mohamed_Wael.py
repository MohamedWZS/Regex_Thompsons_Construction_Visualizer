""" Mohamed Wael 1180383 - language and theory of compilers - Assignment 1 """ 

import json
import graphviz

def missing_bracket_check(userInfix):
	
	stack = []

	for symbol in userInfix:
		# Add the symbol onto the stack if '(' is the current symbol
		if symbol == "(":
			stack.append(symbol)
		# Remove '(' from the stack if the current symbol is ')'
		if symbol == ")":
			stack.pop()

	# At this point the stack should be empty if every opened bracket '(' has a closing one ')'.
	# if not the number of non-closed brackets is number of elements in the stack.
	if len(stack) != 0:
		print(f"Infix Regular Expression missing {len(stack)}  bracket(s)")
		return False 

	print("Infix Regular Expression valid") 
	return True


def shunt_Algo(infix):
	""" The Shunting Yard Algorithm for converting infix(regex) to postfix """
	# Special Character Dict, the numberes resemble the precedence, high number means high precedence
	# Unary Operators have equal precedence
	specials = {
		'*': 50,
		'+': 50,
		'.': 40,
		'|': 30,
	}

	pofix = ""
	stack = ""

	for c in infix:

		if c == '(':
			# Add '(' to operator stack
			stack = stack + c 
		elif c == ')':
			while stack[-1] != '(':
				# We look at the operator stack and pop every operator that is on top of left parenthesis to the output pofix queue
				pofix, stack = pofix + stack[-1], stack[:-1]
			# now we remove the '(' from stack
			stack = stack[:-1]
		elif c in specials:
			# We now need to compare the precedence of current special character with special characters in operator stack
			while stack and specials.get(c, 0) <= specials.get(stack[-1], 0):
				# Add the last item on the stack to pofix, then remove it from the stack 
				pofix, stack = pofix + stack[-1], stack[:-1]
			# Add Character to the stack
			stack += c
		else:
			# Add character to postfix expression
			pofix += c

	while stack:
		# if the stack is not yet empty add the last item ob the stack to postfic, then remove '(' from stack
		pofix, stack = pofix + stack[-1], stack[:-1]

	return pofix


# A state is created with a name called label, two arrows
# "None" means epsilon moves "E"
class state:
	label = None
	edge1 = None
	edge2 = None
	edge1_Label = None
	edge2_label = None


# NFA represented with its initial and accept states
class nfa:
	initial = None
	accept = None

	# initializer
	def __init__(self, initial, accept):
		self.initial = initial
		self.accept = accept


""" Thompson's Construction Algorithm """
def compile(pofix):
	"""Compiles a postfix regular expression into an NFA"""
	id = 0
	nfastack = []
	states = {}

	# Enumerate is used to keep track of the index of the current character in the String
	for i, c in enumerate(pofix):

		# Concatenate
		if c == '.':

			# Pop 2 NFAs off the stack
			nfa2 = nfastack.pop()
			nfa1 = nfastack.pop()
			# Connect first NFAs accept state to the seconds initial state
			nfa1.accept.edge1 = nfa2.initial
			# give the nfa accept state edge a label epsilon
			nfa1.accept.edge1_Label = "Eps"
			# Push the new NFA to the stack
			nfastack.append(nfa(nfa1.initial, nfa2.accept))
			# update the nfa1 accept state and edge label
			if nfa1.accept.label not in states:
				states[nfa1.accept.label] = {}
			states[nfa1.accept.label].update({nfa1.accept.edge1_Label: nfa2.initial.label})


		# 0 or more
		elif c == '*':

			# Pop a single NFA from the stack
			nfa1 = nfastack.pop()
			# Create a new initial state, and give it a label
			initial = state()
			initial.label = "s" + str(id)
			id += 1
			# Create a new accept state, and give it a label
			accept = state()
			accept.label = "s" + str(id)
			id += 1
			# Join the new initial state to nfa1s initial state and to the new accept state
			initial.edge1 = nfa1.initial
			initial.edge2 = accept
			# give the edges their labels
			initial.edge1_Label = "Eps"
			initial.edge2_Label = "Eps"
			# Join the old accept state to the new accept state and to nfa1s initial state
			nfa1.accept.edge1 = nfa1.initial
			nfa1.accept.edge2 = accept
			# give the edges their labels
			nfa1.accept.edge1_Label = "Eps"
			nfa1.accept.edge2_Label = "Eps"
			# Add the new initial state in the states dict if not exist
			if initial.label not in states:
				states[initial.label] = {}
			# Then update the dict with appropraite connection from new created initial state
			# to initial state of nfa1 and the newly created accept state.
			# added the str(number) because in dict keys with the same name replace each other
			states[initial.label].update({initial.edge1_Label + str(1): nfa1.initial.label})
			states[initial.label].update({initial.edge2_Label + str(2): accept.label})
			# Add the new accept state to the states dict if not exist
			if accept.label not in states:
				states[accept.label] = {}
			# Then update the dict with appropraite connection from accept state of nfa1
			# to the new created accept state and a backward connection to nfa1 initial state
			states[nfa1.accept.label].update({nfa1.accept.edge1_Label + str(1): accept.label})
			states[nfa1.accept.label].update({nfa1.accept.edge1_Label + str(2): nfa1.initial.label})
			# make current NFA's initial state the start state of whole NFA for now.
			if len(nfastack) == 0:
				# make current NFA with initial state as the start state
				states.update({"isStartState" : initial.label})
			nfastack.append(nfa(initial, accept))

		# 1 or more
		elif c == '+':

			# Pop a single NFA from the stack
			nfa1 = nfastack.pop()
			# Create a new initial state, and give it a label
			initial = state()
			initial.label = "s" + str(id)
			id += 1
			# Create a new accept state, and give it a label
			accept = state()
			accept.label = "s" + str(id)
			id += 1
			# Join the new initial state to nfa1s initial state only
			initial.edge1 = nfa1.initial
			# give the edges their labels
			initial.edge1_Label = "Eps"
			# Join the old accept state to the new accept state and to nfa1s initial state
			nfa1.accept.edge1 = nfa1.initial
			nfa1.accept.edge2 = accept
			# give the edges their labels
			nfa1.accept.edge1_Label = "Eps"
			nfa1.accept.edge2_Label = "Eps"
			# Add the new initial state in the states dict if not exist
			if initial.label not in states:
				states[initial.label] = {}
			# Then update the dict with appropraite connection from new created initial state
			# to initial state of nfa1.
			# added the str(number) because in dict keys with the same name replace each other
			states[initial.label].update({initial.edge1_Label + str(1): nfa1.initial.label})
			# Add the new accept state to the states dict if not exist
			if accept.label not in states:
				states[accept.label] = {}
			# Then update the dict with appropraite connection from accept state of nfa1
			# to the new created accept state and a backward connection to nfa1 initial state
			states[nfa1.accept.label].update({nfa1.accept.edge1_Label + str(1): accept.label})
			states[nfa1.accept.label].update({nfa1.accept.edge1_Label + str(2): nfa1.initial.label})
			# make current NFA's initial state the start state of whole NFA for now.
			if len(nfastack) == 0:
				# make current NFA with initial state as the start state
				states.update({"isStartState" : initial.label})
			# Push the new NFA to the stack
			nfastack.append(nfa(initial, accept))


		# Or
		elif c == '|':

			# Pop 2 NFAs off the stack
			nfa2 = nfastack.pop()
			nfa1 = nfastack.pop()
			# Create a new initial state, and give it a label
			initial = state()
			initial.label = "s" + str(id)
			id += 1
			# connect it to initial states of the two NFAs popped from the stack
			initial.edge1 = nfa1.initial
			initial.edge2 = nfa2.initial
			# give the edge their labels
			initial.edge1_Label = "Eps"
			initial.edge2_Label = "Eps"
			# Create a new accept state, and give it a label
			accept = state()
			accept.label = "s" + str(id)
			id += 1
			# connecting the accept states of the two NFAs popped from the stack to the new accept state
			nfa1.accept.edge1 = accept
			nfa2.accept.edge1 = accept
			# give the edges their labels
			nfa1.accept.edge1_Label = "Eps"
			nfa2.accept.edge1_Label = "Eps"
			initial.edge1_Label = "Eps"
			initial.edge2_Label = "Eps"
			
			# Add the new initial state in the states dict if not exist
			if initial.label not in states:
				states[initial.label] = {}
			# Then update the dict with appropraite connection from new created initial state
			# to both initial states of nfa1 and nfa2
			# added the str(number) because in dicts keys with the same name replace each other
			states[initial.label].update({initial.edge1_Label + str(1): nfa1.initial.label})
			states[initial.label].update({initial.edge2_Label + str(2): nfa2.initial.label})
			# Add the new accept state to the states dict if not exist
			if accept.label not in states:
				states[accept.label] = {}
			# Then update the dict with appropraite connection from both accept states of nfa1 and nfa2
			# to the new created accept state
			states[nfa1.accept.label].update({nfa1.accept.edge1_Label : accept.label})
			states[nfa2.accept.label].update({nfa2.accept.edge1_Label : accept.label})
			# if stack before pushing current nfa was empty 
			# make current NFA's initial state the start state of whole NFA for now.
			if len(nfastack) == 0:
				# make current NFA with initial state as the start state
				states.update({"isStartState" : initial.label})
			# Push the new NFA to the stack
			nfastack.append(nfa(initial, accept))

		elif c == "$":
			# $ == character set [A-Z]
			# Create new initial and accept states
			accept = state()
			initial = state()
			# Give the initial and accept states their label (eg. s0 and s1)
			initial.label = "s" + str(id)
			id += 1
			accept.label = "s" + str(id)
			id += 1
			# Join the initial state and the accept state using an arrow labelled c
			initial.edge1 = accept
			initial.edge1_Label = c
			# Add the initial state in the states dict if not exist
			if initial.label not in states:
				states[initial.label] = {}
			# Then update the state 
			# Initial.edge1_Label -> 'a' which is the input
			# accept.label -> which is the destination
			# In conclusion (s0 -> s1) where the arrow is 'a'.
			states[initial.label].update({initial.edge1_Label : accept.label})
			# states[initial.label].update({initial.edge2_label : None})
			# Add the accept state to the states dict if not exist
			if accept.label not in states:
				states[accept.label] = {}
			# if stack before pushing current nfa was empty 
			# make current NFA's initial state the start state of whole NFA for now.
			if len(nfastack) == 0:
				states.update({"isStartState" : initial.label})
			# Push the new NFA to the stack
			nfastack.append(nfa(initial, accept))

		else:
			# Create new initial and accept states
			accept = state()
			initial = state()
			# Give the initial and accept states their label (eg. s0 and s1)
			initial.label = "s" + str(id)
			id += 1
			accept.label = "s" + str(id)
			id += 1
			# Join the initial state and the accept state using an arrow labelled c
			initial.edge1 = accept
			initial.edge1_Label = c
			# Add the initial state in the states dict if not exist
			if initial.label not in states:
				states[initial.label] = {}
			# Then update the state 
			# Initial.edge1_Label -> 'a' which is the input
			# accept.label -> which is the destination
			# In conclusion (s0 -> s1) where the arrow is 'a'.
			states[initial.label].update({initial.edge1_Label : accept.label})
			# states[initial.label].update({initial.edge2_label : None})
			# Add the accept state to the states dict if not exist
			if accept.label not in states:
				states[accept.label] = {}
			# if stack before pushing current nfa was empty 
			# make current NFA's initial state the start state of whole NFA for now.
			if len(nfastack) == 0:
				states.update({"isStartState" : initial.label})
			# Push the new NFA to the stack
			nfastack.append(nfa(initial, accept))

	# Add indicator entry for the terminating state
	for key, value in states.items():
		# At this point the terminating state is the only state that has an empty dict as value.
		if len(value) == 0:
			states[key] = {"isTerminatingState": True}

    # nfastack should only have a single nfa on it at this point
	# return nfastack.pop()
	return states

# draw the states we compiled as nodes
def draw_states(states):

	G = graphviz.Digraph('test', format='png')

	# Create nodes
	for state, destinationInfo in states.items():

		if state == "isStartState":
			continue

		if "isTerminatingState" in destinationInfo:
			G.node(state, shape = 'doublecircle')
		else:
			G.node(state, shape = 'circle')

	# Create edges
	for state, destinationInfo in states.items():

		if state == "isStartState":
				continue

		for item in destinationInfo:

			if item == "isTerminatingState":
				continue
			G.edge(state, destinationInfo[item], label=item)


	G.render('NFA')

if __name__ == "__main__":

	print( """
		[1] to concatenate use '.' dot operator eg = a.b.c \n
		[2] to union use '|' pipeline operator eg = (a|b|c) \n
		[3] to use kleene star '*' eg = (((a.b|c).d))* \n
		[4] to use Plus operator '+' eg = (((a.b|c).d))+ \n
		[5] to use character set a '$' dollar sign is used instead.\n 
		[6] the empty state is the accept state in json printout.

		# to terminate press '~' telda sign.
	""")
	
	while (True):
	
		# promp the user to enter the infix(regex)
		userInfix = input("Enter an Infix Regular Expression (eg. ab*): ")

		# Terminating sign
		if userInfix == '`':
			print("program terminated")
			break

		# check for pair brackets
		elif missing_bracket_check(userInfix):

			# run the Shunt & Thompson's Algo on the Infix
			finalStates = compile(shunt_Algo(userInfix))

			# write the output in json object then print it
			jsonObject = json.dumps(finalStates, indent = 4)
			print(jsonObject, "\n")

			# Output the json file
			with open("output.json", "w") as outfile:
				outfile.write(jsonObject)

			# show the plot
			draw_states(finalStates)
