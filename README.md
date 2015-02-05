# myown_typecheker
Linear Type Checker for MyOwn Language

Implementation of a Linear Type Checker, where taint and untaint are considered as linear and non-linear types respectively. Type Checker mimics static taint propogation, where typing rules are taint rules.

Refer Docs for more details.

Costom imperative language (named myown) is used. Its a minimal subset of C.

Refer docs/myown_grammer for grammer and tests for examples.

## Usage
	python main.py -f file_to_be_typechecked

## Requirements:
	>= Python 2.7
	Python Package: ply  
	
