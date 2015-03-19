# myown_typechecker
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
	
## Source code Organization:
All sources are present under src folder.
Lexer: src/lexer.py
Parser: src/parser.py
TypeChecker: src/type_checker.py
    
## Tests:
All tests are present under tests folder.
    
To run a test:
    python src/main.py -f tests/typechecker_fails/simple_if_taint.myown
    
Negative tests are under: tests/typechecker_fails these contain cases where programs are incorrectly typed. 
Corresponding correctly typed programs are located under: tests/typechecker_passes folder.
    
Example: type checker fails for file: tests/typechecker_fails/simple_if_taint.myown, as it is incorrectly typed. Where as corresponding file in folder typechecker_passes i.e tests/typechecker_passes/simple_if_taint.myown contains fixed version of the same code and it passes type checker.
	
