#!/usr/bin/env python
import remoter
import socket
from flask import Flask, request, render_template
from flask_frozen import Freezer
import os, subprocess, sys
import json



# ==================================	Argument Parser
import argparse

parser = argparse.ArgumentParser( description = "A tool for remote system enumeration" )

parser.add_argument("--command-file", '-f', help = "The file that contains the commands to run on the remote system in JSON format" )
parser.add_argument("--command-dir", '-d', help = "The directory that contains the command files", default = "./commands")
parser.add_argument("-P", help = "Port were the %s WebPage will be served" % sys.argv[0], type = int, default = 8085)
subparsers = parser.add_subparsers( help = "The connection type with the remote host", dest='command')

localhost_parser = subparsers.add_parser("local")

ssh_parser = subparsers.add_parser("ssh")
ssh_parser.add_argument("SSH_connection", default = "user@172.0.0.1",\
						 help = "SSH connection string. example: 'user@address'")
ssh_parser.add_argument("--port", '-p', help = "TCP port to SSH (default: 22)", default = 22, type = int)


bind_parser = subparsers.add_parser("bind")
bind_parser.add_argument("IP", help = "The IP address of the remote host")
bind_parser.add_argument("--port", '-p', help = "TCP port to connect (default: 4444)", default = 4444, type = int)


reverse_parser = subparsers.add_parser("reverse")
reverse_parser.add_argument("--port", '-p', help = "TCP port to wait for the shell (default: 4444)", default = 4444, type = int)


args = parser.parse_args()

# ==================================
# print args



# ==================================	Command Loader
# '''
command_directory = args.command_dir

command_array = []

for filename in sorted( os.listdir(command_directory) ) :
	file = command_directory + os.sep + filename
	if os.path.isfile( file ) and file.endswith('.json') :
		jsonDict = json.load( open( file ) )
		jsonDict['filename'] = filename
		command_array.append( jsonDict )

from pprint import pprint
# pprint(command_array)
# '''

# ==================================


client = None
def runSocketCommand( comm ) :
	client.send( ' ' + comm + '\n')
	return client.recv(512)

def runLocalhostCommand( comm ) :
	return os.popen( comm ).read()

# SSH pending
# print args

# ==================================	Socket Creator

if args.command == "bind" :
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	address = (args.IP, args.port )
	client.connect( address )
	runCommand = runSocketCommand


elif args.command == "reverse" :
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind( ("0.0.0.0", args.port ) )
	print "Waiting for the Reverse Shell at port %d" % args.port
	try :
		server.listen(5)
	except KeyboardInterrupt :
		print "Aborted by user..."
		sys.exit(-2)
	client, address = server.accept()
	runCommand = runSocketCommand


elif args.command == "local" :
	runCommand = runLocalhostCommand



# ==================================







# ==================================	Command Runner
metaDict = {}
metaDict['version'] = remoter.version
metaDict['cli'] = ' '.join(sys.argv)

for command_list in command_array :

	# print command_list
	for command in command_list['commands'] :

		response = runCommand( command['command'] )
		if 'tag' in command :
			metaDict[ command['tag'] ] = response
		# print command['command']
		# print response
		# print

		command['response'] = response

# ==================================




# ==================================	WebApp Initializer
template_folder=os.path.abspath("webresources/templates")
app = Flask( __name__, template_folder = template_folder )


@app.route('/')
def index() :
    return render_template("index.html", command_array = command_array, meta = metaDict)


@app.route('/groups')
def groupsPage() :
    return render_template("groups.html", command_array = command_array)


@app.route('/command/<filename>')
def commandsPage( filename = filename ) :
	for comm_list in command_array[::-1] :
		if filename == comm_list['filename'] :
			break
	print filename
	return render_template("commands.html", comm_list = comm_list, meta = metaDict )


@app.route('/commands')
def commandListPage() :
    return render_template("command_list.html", command_array = command_array)

@app.route('/search/', methods = ['POST'])
def searchPage() :
	if request.method != 'POST':
		return index()
	data = request.form
	if 'keyword' not in data :
		return index()
	keyword = data['keyword']
	ret = {}
	ret['commands'] = []
	for command_list in command_array :
		for command in command_list['commands'] :
			if keyword in ' '.join( command.values() ) :
				ret['commands'].append( command )
	ret['name'] = 'Search for keyword "%s" - %d results' % (keyword, len( ret['commands'] ))
	return render_template("commands.html", comm_list = ret, meta = metaDict )

# ==================================





if __name__ == '__main__':
	flask_port = args.P
	os.system(" firefox http://localhost:%d &" % flask_port)
	app.run( port = flask_port )



