
import sys, os
import json


D = dict()

for file in os.listdir( sys.argv[1] ) :

	f_name = file
	file  = sys.argv[1] + '/' + file
	text = open(file, 'r').readlines()
	commands = []
	descs = []

	name = text[0].strip().split('=')[1][1:-2]
	comms = True
	for line in text[1:] :
		if not line : continue
		if '"' in line and comms :
			commands.append( ''.join( line.strip()[1:-1] ).strip() )
		elif '"' in line and not comms :
			descs.append( ''.join(line.strip()[1:-1]).strip() )

		if "_desc" in line :
			comms = False

	print name
	print zip(commands, descs)

	com_dict = {}
	com_dict["commands"] = [ { "command" : item[0], "description" : item[1]} for item in zip(commands, descs) ]

	com_dict["name"] = name

	print
	print
	print

	toDump = open("./commands/%s.json" % f_name, 'w')
	toDump.write( json.dumps( com_dict, indent = 2 ) )
	print com_dict
	toDump.close()

# for v in D.values() :
# 	print json.dumps(v, indent = 2)