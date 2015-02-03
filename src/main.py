from parser import MyOwnParser
from ast.c_ast import *
import os
from type_checker import LinearTaintChecker
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='target_src_file', required = True,help='Path to the myown src file')
    parser.add_argument('-d', dest='debug_mode', action='store_true', default=False, help='Debug mode: Expect lot of output')
    parsed_args = parser.parse_args()
    target_src_file = parsed_args.target_src_file
    debug_mode = parsed_args.debug_mode
    
    if os.path.isfile(target_src_file):
        f_d = open(target_src_file,'r')
        file_data = f_d.read()
        newparser = MyOwnParser()
        ast_nodes = newparser.parse(file_data)
        type_check = LinearTaintChecker(['taint'],['untaint'],debug=debug_mode)
        ret_val = type_check.do_type_checking(ast_nodes)
        if ret_val:
            print 'TypeChecking Passed for file:' + target_src_file
        else:
            print 'TypeChecking Failed for file:' + target_src_file
    else:
        print 'Error: Provided file:' + str(target_src_file) + ' doesn\'t exist'
    
if __name__ == '__main__':
    sys.exit(main())
