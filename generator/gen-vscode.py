#!/usr/bin/env python
import json
import sys
import os
import string

scriptpath = os.path.dirname(os.path.realpath(sys.argv[0]))

with open(scriptpath + '/mpi.json') as data_file:
	mpi_interface = json.load(data_file)


IFACE="{"

for f in mpi_interface:
	fd = mpi_interface[f]
	rtype=""
	if(f=="MPI_Wtime"):
		rtype = "double"
	else:
		rtype = "int"
	IFACE+= "\n\"" + f + "\": {\n"
	IFACE+= "\t\"scope\": \"c,cpp\",\n"
	IFACE+= "\t\"prefix\": [\""+f+"\"],\n"
	IFACE+= "\t\"description\" : \"MPI " + f.replace("MPI_", "") + " Snippet\",\n"
	IFACE+= "\t\"body\" : [ \"" + f + "("
	for i in range(0, len(fd)):
		arg=fd[i]
		name = arg[1];
		ctype = arg[0];
		#ARRAY CASE
		array=""
		try:
			idx=ctype.index("[")
		except ValueError:
			idx=-1
		if idx!=-1:
			array=ctype[idx:]
			ctype=ctype[0:idx]
		IFACE+=" ${" + str(i+1) + ":" + ctype + " " + name + array + "}"
		if i < (len(fd) - 1):
			IFACE += " ,"

	IFACE+= ");\"]\n"
	IFACE+="},\n"

#This is the static part
IFACE += """
"Main() MPI" : {
    "scope" : "c,cpp",
	"prefix" : ["mainmpi", "mpimain", "mpi-main" ],
	"description": "Generate a basic MPI program",
	"body" : [
"#include <mpi.h>",
"",
"int main( int argc, char *argv[])",
"{",
"\\tint rank, size;",
"\\tMPI_Init(&argc, &argv);",
"\\tMPI_Comm_rank(MPI_COMM_WORLD, &rank);",
"\\tMPI_Comm_size(MPI_COMM_WORLD, &size);",
"\\t",
"\\t${1:printf(\\"Rank: %d/%d\\\\n\\", rank, size);}",
"\\t",
"\\tMPI_Finalize();",
"\\t",
"\\treturn 0;",
"}"
]},

"Comm Self": {
	"scope" : "c,cpp",
	"prefix": ["cself", "CS"],
	"description": "Expand to MPI_COMM_SELF",
	"body" : "MPI_COMM_SELF"
},

"Comm World": {
    "scope" : "c,cpp",
	"prefix": ["cworld", "CW"],
	"description": "Expand to MPI_COMM_WORLD",
	"body" : "MPI_COMM_WORLD"
},
"""


IFACE+="}\n"
f = open(scriptpath + "/../src/mpi.code-snippets", "w" )
f.write( IFACE );

f.close()
