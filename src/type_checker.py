from ast.c_ast import *

class LinearTaintChecker(object):
    def __init__(self,linear_types,non_linear_types,debug=False):
        self.TAG = 'LinearTaintChecker:'
        self.var_type_name = 'variables'
        self.func_type_name = 'functions'
        self.debug = debug
        self.allowed_force_assignment = ['FuncCall']
        self.assumptions = {}
        self.initialize_assumptions(self.assumptions)
        self.linear_types = linear_types[:]
        self.non_linear_types = non_linear_types[:]
        
        #current function under evaluvation
        self.curr_function = None

    def do_type_checking(self, top_ast_node):
        to_ret = True
        for curr_node in top_ast_node:
            (curr_node_ret,curr_node_fine) = self.verify_ast_node(curr_node,self.assumptions)
            if not curr_node_fine:
                print 'Error occured while Type Checking:' + str(curr_node)
                to_ret = False
                break
                
        return to_ret
    
    # logging
    
    def __debug_msg(self,msg):
        if self.debug:
            print self.TAG + msg
    
    def __error_msg(self,msg):
        print self.TAG + ' TYPECHECK_FAILED:'+ msg
        
    def __internal_error_msg(self,msg):
        print self.TAG +' INTERNAL ERROR:' + msg

    # initialization
    
    def initialize_assumptions(self,new_assumptions):
        new_assumptions[self.var_type_name] = {}
        new_assumptions[self.func_type_name] = {}

    
    # Helper functions
    
    def get_variable_type(self,var_name,assumptions):
        to_ret = None
        if self.var_type_name in assumptions:
            if var_name in assumptions[self.var_type_name]:
                to_ret = assumptions[self.var_type_name][var_name]
        
        return to_ret
    
    def remove_variable_type(self,var_name,assumptions):
        to_ret = False
        if self.var_type_name in assumptions:
            if var_name in assumptions[self.var_type_name]:
                del assumptions[self.var_type_name][var_name]
                to_ret = True
        
        return to_ret
        
    def insert_variable_type(self,var_name,type_name,assumptions,force=False):
        to_ret = False
        self.__debug_msg('In insert variable for:' + var_name + ' type:' + type_name + ' results:' + str(assumptions))
        if force:
            self.remove_variable_type(var_name,assumptions)
        if self.var_type_name in assumptions:
            if not (var_name in assumptions[self.var_type_name]):
                self.__debug_msg('Inserting Type')
                assumptions[self.var_type_name][var_name] = type_name
                to_ret = True
        
        return to_ret

    '''
        Returns flag indicating whether redeclaration is allowed from old_type to new_type
    '''
    def is_redeclaration_allowed(self,old_type,new_type):
        to_ret = False
        if (old_type == new_type) or ((old_type in self.non_linear_types) and (new_type in self.linear_types)):
            to_ret = True
        return to_ret
        
    def is_linear_type(self,target_type):
        return target_type in self.linear_types
        
    def get_constant_type(self):
        return self.non_linear_types[0]
    
    '''
        Merge the provided types
    '''
    def merge_types(self,type1,type2):
        target_type = None
        if type1 == type2:
            target_type = type1
        elif self.is_linear_type(type1) and (not self.is_linear_type(type2)):
            target_type = type1
        elif self.is_linear_type(type2) and (not self.is_linear_type(type1)):
            target_type = type2
        return target_type

    '''
        Returns target type of the left, given left and right.
    '''
    def get_assignment_type(self,ltype,rtype):
        to_ret = None
        if ltype == rtype:
            to_ret = ltype
        if (not self.is_linear_type(ltype)) and self.is_linear_type(rtype):
            to_ret = rtype
        return to_ret
    
    '''
        Function than implements visitor pattern on AST nodes
    '''
    def verify_ast_node(self,ast_node,assumptions):
        target_type = ast_node.__class__.__name__
        target_method_name = 'verify_' + target_type
        self.__debug_msg('Called verify ast:' + str(ast_node) +' Location:' + str(ast_node.coord))
        target_method = getattr(self, target_method_name)
        self.__debug_msg('In verify_ast_node:' + target_method_name)
        ret_val = target_method(ast_node,assumptions)
        self.__debug_msg('In varify_ast_node: end,' + str(ret_val))
        return ret_val
    
    '''
        Returns flag indicating whether the function is defined or not.
    '''
    def has_func_definition(self,func_decl,assumptions):
        to_ret = False
        if self.func_type_name in assumptions:
            if func_decl.name in assumptions[self.func_type_name]:
                to_ret = assumptions[self.func_type_name]['defined']
        return to_ret
        
    '''
        get function signature.
    '''
    def get_func_declaration(self,func_name,assumptions):
        to_ret = None
        if self.func_type_name in assumptions:
            self.__debug_msg('Checking decl of:' + func_name + ' in ' + str(assumptions[self.func_type_name]))
            if func_name in assumptions[self.func_type_name]:                
                to_ret = assumptions[self.func_type_name][func_name]
        self.__debug_msg('Returning:' + str(to_ret))
        return to_ret
    
    '''
        gets return type of function from assumptions.
    '''
    def get_func_return_type(self,func_name,assumptions):
        to_ret = None
        func_decl = self.get_func_declaration(func_name,assumptions)
        if func_decl:
            to_ret = func_decl['ret_type']
        return to_ret
    
    '''
        Inserts provided function declaration into assumptions.
    '''
    def insert_func_declartion(self,func_decl,assumptions,force=False):
        to_ret = False
        func_name = func_decl.name
        if force:
            self.remove_func_declartion(func_decl,assumptions)
        if self.func_type_name in assumptions:
            self.__debug_msg('Trying to insert declaration:' + func_name)
            if not (func_name in assumptions[self.func_type_name]):
                seen_var_names = []
                args_types = []
                for curr_arg in func_decl.args.decls:
                    if not (curr_arg.name in seen_var_names):
                        seen_var_names.append(curr_arg.name)
                        args_types.append(curr_arg.typename)
                    else:
                        self.__error_msg('Error: duplicate variable names in function parameter:' + str(curr_arg.name))
                        seen_var_names = None
                        break
                if seen_var_names != None:
                    assumptions[self.func_type_name][func_name] = {}
                    assumptions[self.func_type_name][func_name]['ret_type'] = func_decl.type
                    assumptions[self.func_type_name][func_name]['args_type'] = args_types
                    assumptions[self.func_type_name][func_name]['defined'] = False
                    to_ret = True
                    self.__debug_msg('Setting True')
                    
        return to_ret

    '''
        Sets function defined as true
    '''
    def insert_func_definition(self,func_decl,assumptions):
        func_name = func_decl.name
        assumptions[self.func_type_name][func_name]['defined'] = True
        return True
            
    
    '''
        Check for a match of the provided declaration in assumptions.
    '''
    def match_function_declaration(self,func_decl,assumptions):
        to_ret = False
        available_decl = self.get_func_declaration(func_decl.name,assumptions)
        if available_decl:
            if not (available_decl['ret_type'] == func_decl.type):
                self.__error_msg('Error:  expected return type:' + available_decl['ret_type'] +' but got:' + func_decl.type)
            else:
                seen_var_names = []
                args_types = []
                for curr_arg in func_decl.args.decls:
                    if not (curr_arg.name in seen_var_names):
                        seen_var_names.append(curr_arg.name)
                        args_types.append(curr_arg.typename)
                    else:
                        self.__error_msg('Error: duplicate variable names in function parameter:' + str(curr_arg.name))
                        seen_var_names = None
                        break
                if seen_var_names != None:
                    if len(args_types) == len(func_decl.args.decls):
                        to_ret = True
                        i = 0
                        for curr_arg in func_decl.args.decls:
                            if args_types[i] != curr_arg.typename:
                                to_ret = False
                                break
                            i += 1
                else:
                    self.__internal_error_msg('Error occured while checking variable names')    
        return to_ret
    
    '''
        This function verifies list of statements
    '''
    def verify_statement_list(self,statms,assumptions):
        self.__debug_msg('Verifying statement_list:' + str(statms))
        to_ret = None
        all_fine = False
        if len(statms) == 0:
            all_fine = True
        for curr_stat in statms:
            self.__debug_msg('statement:' + str(curr_stat))
            (curr_stat_ret,curr_stat_fine) = self.verify_ast_node(curr_stat,assumptions)
            self.__debug_msg('End statement:' + str(curr_stat))
            to_ret = curr_stat_ret
            all_fine = curr_stat_fine
            if not curr_stat_fine:
                self.__error_msg('Error: verifying statememnt:' + str(curr_stat) +'\n Available assumptions:' + str(assumptions))
                to_ret = None
                break
        return (to_ret,all_fine)
    
    
    # AST Verifier Functions 
    
    '''
        This verifies Function Call.
        1) Checks if type of arguments are compatable with parameter types.
        2) if the function return type if non linear, removes the taint assumptions of the argument types.
    '''
    def verify_FuncCall(self,ast_node,assumptions):
        self.__debug_msg('Verifying FuncCall:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        to_ret = None
        all_fine = False
        args_key = 'args_type'
        target_func = self.get_func_declaration(ast_node.name,assumptions)
        if target_func:
            if len(target_func[args_key]) == len(ast_node.args):
                i = 0
                # check if arguments are compatable with parameter types
                args_fine = True
                for curr_arg in ast_node.args:
                    (arg_ret,arg_fine) = self.verify_ast_node(curr_arg,assumptions)
                    if arg_fine:
                        if not (arg_ret == target_func[args_key][i] or ((not self.is_linear_type(arg_ret)) and self.is_linear_type(target_func[args_key][i]))):
                            self.__error_msg('Error: Expected argument type:' + target_func[args_key][i] + ' got:'+arg_ret + ' at:' + str(ast_node.coord))
                            args_fine = False
                            break
                    else:
                        args_fine = False
                        self.__error_msg('Error: Unable to get type for argument:' + curr_arg.name +'\nAvailable Assumptions:' + str(assumptions))
                        break                            
                    i += 1
                if args_fine:
                    if not self.is_linear_type(target_func['ret_type']):
                        #if return type is non linear type we need to remove linear type mappings for variables.
                        for curr_arg in ast_node.args:
                            (arg_ret,arg_fine) = self.verify_ast_node(curr_arg,assumptions)
                            if arg_fine and self.is_linear_type(arg_ret):
                                self.remove_variable_type(curr_arg.name,assumptions)
                    all_fine = True
                    to_ret = target_func['ret_type']
            else:
                self.__error_msg('Error: incorrect number of arguments, expected:' + str(len(target_func[args_key])) + ' got:' + str(len(ast_node.args)))
        else:
            self.__error_msg('Error: unrecognized function:' + ast_node.name + '\n Available assumptions:' + str(assumptions))
            
        return (to_ret,all_fine)
    
    '''
        This verifies Function Declaration.
        1) Checks if the declaration already exists, if yes then throws error.
        2) Else inserts the function name, return type, and arguments type into assumption.
    '''
    def verify_FuncDecl(self,ast_node,assumptions):
        self.__debug_msg('Verifying FuncDecl:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        to_ret = None
        all_fine = False
        if not self.get_func_declaration(ast_node.name,assumptions):
                self.__debug_msg('Trying to insert function declaration:' + ast_node.name)
                all_fine = self.insert_func_declartion(ast_node,assumptions)
                if not all_fine:
                    self.__internal_error_msg('Unable to insert function declartion of function:' + ast_node.name + ' at:' + str(ast_node.coord) + '\n Available assumptions:' + str(assumptions))
        else:
                self.__error_msg('Error: Redeclaration of function:' + ast_node.name)
        return (to_ret,all_fine)
    
    '''
        This verifies If statement.
        1) It checks the type of condition.
        2) Throws error if the condition is a linear type.
        3) verifies body
    '''
    def verify_If(self,ast_node,assumptions):
        self.__debug_msg('Verifying If:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        to_ret = None
        all_fine = False
        (cond_ret,cond_fine) = self.verify_ast_node(ast_node.cond,assumptions)
        if cond_fine:
            #condition should not be linear type
            if self.is_linear_type(cond_ret):
                self.__error_msg('Error: Linear Type in If condition; Expected non-linear type, at'+ str(ast_node.coord))
            else:
                (to_ret,all_fine) = self.verify_statement_list(ast_node.iftrue,assumptions)   
            
        return (to_ret,all_fine)
    
    '''
        This verifies Function Definition.
        1) It inserts function signature, if not present.
        2) Checks if existing signature is same as signature in the definition.
        3) Creats a set of new assumptions with parameter names and types.
        4) Type checks body.
    '''
    def verify_FuncDef(self,ast_node,assumptions):
        self.__debug_msg('Verifying FuncDef:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        to_ret = None
        all_fine = False
        self.__debug_msg('Checking FuncDef:' + str(ast_node))
        if self.has_func_definition(ast_node.decl,assumptions):
            self.__error_msg('Error: Redefinition of function:' + ast_node.decl.name +' Detected. Type Check Failed.')
        else:           
            if not self.get_func_declaration(ast_node.decl.name,assumptions):
                self.insert_func_declartion(ast_node.decl,assumptions)
            if self.match_function_declaration(ast_node.decl,assumptions):
                #mark the function as defined.
                self.insert_func_definition(ast_node.decl,assumptions)
                new_assumptions = {}
                self.initialize_assumptions(new_assumptions)
                #add function assumptions
                new_assumptions[self.func_type_name] = assumptions[self.func_type_name].copy()
                
                #Insert paramter types into new_assumptions
                for curr_var in ast_node.decl.args.decls:
                    curr_var_name = curr_var.name
                    curr_var_type = curr_var.typename
                    self.insert_variable_type(curr_var_name,curr_var_type,new_assumptions)
                
                
                self.curr_function = ast_node.decl.name
                self.__debug_msg('Verifying Statements')
                (to_ret,all_fine) = self.verify_statement_list(ast_node.body,new_assumptions)
                self.curr_function = None
        return (to_ret,all_fine)

    '''
        This verifies Declaration list, i.e list of Decls.
        
    '''
    def verify_DeclList(self,ast_node,assumptions):
        self.__debug_msg('Verifying DeclList:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        to_ret = None
        all_fine = False
        original_assumptions = assumptions[:]
        for curr_dec in ast_node.decls:
            (to_ret,all_fine) = self.verify_ast_node(curr_dec,assumptions)
            if not all_fine:
                to_ret = None
                self.__error_msg('Unable to get type for declaration at:' + str(curr_dec.coord) + '\n Available assumptions:' + str(assumptions))
                del assumptions[:]
                assumptions.extend(original_assumptions)
                break
                
        return (to_ret,all_fine)
    
    '''
        This verifies a variable, basically it checks for available type in assumptions.
    '''
    def verify_ID(self,ast_node,assumptions):
        self.__debug_msg('Verifying ID:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        to_ret = None
        all_fine = False
        to_ret = self.get_variable_type(ast_node.name,assumptions)
        if to_ret:
            all_fine = True
        else:
            self.__error_msg('Unable to get type for:' + str(ast_node.name) + ' at:'+str(ast_node.coord) +'\n Available assumptions:' + str(assumptions))
        return (to_ret,all_fine)
    
    '''
        This verifies Variable declaration.
        If the variable is redeclared, it checks for compatable types: non-linear -> linear or of same type.
        or in case of in-compatable redeclaration, it errors out.
    '''
    def verify_Decl(self,ast_node,assumptions):
        self.__debug_msg('Verifying Decl:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        all_fine = False
        to_ret = None
        #get the current type of the variable.
        curr_type = self.get_variable_type(ast_node.name,assumptions)
        # if its not declared or it can be redeclared, then proceed
        if (not curr_type) or (self.is_redeclaration_allowed(curr_type,ast_node.typename)):
            self.__debug_msg('Verifying Decl:' + str(ast_node) + ' inserting for:' + str(ast_node.typename))
            all_fine = self.insert_variable_type(ast_node.name,ast_node.typename,assumptions,force=True)
            to_ret = ast_node.typename   
            self.__debug_msg('Verifying Decl:' + str(ast_node) + ' inserting end for:' + str(ast_node.typename) + ' return:' + str(to_ret) + ' all_fine:' + str(all_fine))
        else:
            self.__error_msg('Redeclartion not allowed for type:' + str(curr_type) + ' for variable:' + str(ast_node.name) + ' \n Available assumptions:' + str(assumptions))

        self.__debug_msg('Verifying Decl Returning:' + str(to_ret) + ' fine:' + str(all_fine) +' For:' + str(ast_node))
        return (to_ret,all_fine)

    '''
        This verifies String Constant.
        Just assigns an non-linear type to it.
    '''
    def verify_StringConstant(self,ast_node,assumptions):
        self.__debug_msg('Verifying StringConstant:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        to_ret = None
        all_fine = False
        #get a non-linear type
        to_ret = self.get_constant_type()
        if to_ret:
            all_fine = True
        else:
            self.__internal_error_msg('Problem occured while trying to get string constant type for:' + str(ast_node.value))
        return (to_ret,all_fine)
        
    '''
        This verifies Integer Constant.
        Just assigns an non-linear type to it.
    '''
    def verify_IntConstant(self,ast_node,assumptions):
        self.__debug_msg('Verifying IntConstant:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        to_ret = None
        all_fine = False
        #get a non-linear type
        to_ret = self.get_constant_type()
        if to_ret:
            all_fine = True
        else:
            self.__internal_error_msg('Problem occured while trying to get string constant type for:' + str(ast_node.value))
        return (to_ret,all_fine)
    
    '''
        This verifies Type of the binary expression.
            1) Gets the type of left and right expression.
            2) merges the types : (linear <op> non-linear) = linear
            3) returns the merged type
    '''
    def verify_BinaryOp(self,ast_node,assumptions):
        self.__debug_msg('Verifying BinaryOp:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        #get type of left
        (left_ret,left_fine) = self.verify_ast_node(ast_node.left,assumptions)
        all_fine = left_fine
        to_ret = left_ret
        if left_fine and ast_node.right:
            all_fine = False
            to_ret = None
            # get type of right
            (right_ret,right_fine) = self.verify_ast_node(ast_node.right,assumptions)
            if right_fine:     
                #merge the types           
                to_ret = self.merge_types(left_ret,right_ret)
                if to_ret:
                    all_fine = True
                else:
                    self.__internal_error_msg('Problem occured while trying to merge types:' + str(left_ret) + ' and ' + str(right_ret))
            else:
                self.__error_msg('Unable to typecheck right of the assignment at:' + str(ast_node.right.coord) +'\n Available Assumptions:' + str(assumptions))
        else:
            self.__error_msg('Unable to typecheck left of the assignment at:' + str(ast_node.left.coord) +'\n Available Assumptions:' + str(assumptions))    
        return (to_ret,all_fine)
        
    
    '''
        This verifies Assignment statement.
        It gets the type of the right hand and left hand, checks if they are assignment compatable. i.e linear -> linear, nonlinear->nonlinear or nonlinear->linear
        if yes, it changes the type of the left hand id to the right hand type.
            
    '''
    def verify_Assignment(self,ast_node,assumptions):
    
        self.__debug_msg('Verifying Assignment:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        
        #get the type of lvalue
        (left_ret,left_fine) = self.verify_ast_node(ast_node.lvalue,assumptions)
        all_fine = left_fine
        to_ret = left_ret
        if left_fine and ast_node.rvalue:
            all_fine = False
            to_ret = None
            #get the type of rvalue
            (right_ret,right_fine) = self.verify_ast_node(ast_node.rvalue,assumptions)
            if right_fine:
                '''right_node_name = ast_node.rvalue.__class__.__name__
                if right_node_name in self.allowed_force_assignment:
                    # if force assignment is allowed                    
                    self.__debug_msg('Allowing Force assignment as function retunes non-linear type')
                    target_type = right_ret
                else:'''
                target_type = self.get_assignment_type(left_ret,right_ret)
                if target_type:
                    all_fine = self.insert_variable_type(ast_node.lvalue.name,target_type,assumptions,force=True)
                    if all_fine:
                        to_ret = target_type
                    else:
                         self.__internal_error_msg('Internal Error, problem occured while inserting new type from Assignment')
                else:
                    self.__error_msg('Error: cannot assign :' + right_ret + ' to ' + left_ret + ' at' + str(ast_node.coord))
        return (to_ret,all_fine)


    '''
        This verifies Return statement.
        It checks the type of the return value to be compatable with the corresponding function return type
    '''        
    def verify_Return(self,ast_node,assumptions):
        self.__debug_msg('Verifying Return:' + str(ast_node) + ' at line:' + str(ast_node.coord))
        all_fine = False
        to_ret = None
        # get the type of the return expression
        (expr_ret,expr_fine) = self.verify_ast_node(ast_node.expr,assumptions)
        if expr_fine:
            if self.curr_function:
                #get the return type and match it.
                func_ret_type = self.get_func_return_type(self.curr_function,assumptions)
                if not func_ret_type:
                    self.__internal_error_msg('Unable to get return type of the current function:' + self.curr_function)
                else:
                    target_ret_type = self.get_assignment_type(expr_ret,func_ret_type)
                    to_ret = target_ret_type
                    if not target_ret_type:
                        self.__error_msg('Incompatable type of return expression, expected:' + func_ret_type+' got:' + expr_ret +' at' + str(ast_node.coord))
                    else:
                        all_fine = True
            else:
                self.__internal_error_msg('No current function found. self.curr_function is None')                
        else:
            self.__error_msg('Unable to get type of the expression provided in return at:' + str(ast_node.coord) +'\n Available Assumptions:' + str(assumptions))

        return (to_ret,all_fine)
