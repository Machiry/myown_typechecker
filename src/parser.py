from plyparser import PLYParser, Coord, ParseError
import ply.yacc as yacc
from ast.c_ast import *
from lexer import MyOwnLexer

class MyOwnParser(PLYParser):
    def __init__(self):
        self.TAG = 'MyOwnParser:'
            
        self.mylex = MyOwnLexer()

        self.mylex.build(
            optimize=False,
            lextab='myownparser.lextab')
        self.tokens = self.mylex.tokens

        self.myparser = yacc.yacc(
            module=self,
            start='translation_unit_or_empty',
            debug=False,
            optimize=False,
            tabmodule='myownparser.yacctab')

        # Keeps track of the last token given to yacc (the lookahead token)
        self._last_yielded_token = None

    def parse(self, text, filename='', debuglevel=0):
        """ Parses myown code and returns an AST.

            text:
                A string containing the myown source code

            filename:
                Name of the file being parsed (for meaningful
                error messages)

            debuglevel:
                Debug level to yacc
        """
        self.mylex.filename = filename
        self.mylex.reset_lineno()
        self._last_yielded_token = None
        return self.myparser.parse(
                input=text,
                lexer=self.mylex,
                debug=debuglevel)        

    def p_translation_unit_or_empty(self,p):
        ''' translation_unit_or_empty   : translation_unit
                                    | empty
        '''
        #print "p_translation_unit_or_empty"
        if p[1]:
            if len(p[1]) > 1:
                p[0] = p[1]
            else:
                p[0] = [p[1]]
        else:
            p[0] = None

    def p_translation_unit_1(self,p):
        ''' translation_unit : external_declaration
        '''
        #print "p_translation_unit_1"
        #statments = []
        p[0] = p[1]

    def p_translation_unit_2(self,p):
       ''' translation_unit    : translation_unit external_declaration
       '''
       #print "p_translation_unit_2"
       i = 1
       statements = []
       while i < len(p):
        if isinstance(p[i],list):
            statements.extend(p[i])
        else:
            statements.append(p[i])
        i += 1
       p[0] = statements

    def p_external_declaration_1(self,p):
        ''' external_declaration : function_declaration
        '''
        p[0] = p[1]

    def p_external_declaration_2(self,p):
        ''' external_declaration : function_definition
        '''
        p[0] = p[1]

    def p_function_definition(self,p):
        ''' function_definition : func_decl LBRACE statement RBRACE
        '''
        #print 'p_function_definition'
        p[0] = FuncDef(p[1],p[3],coord=p[3][0].coord)

    def p_statement(self,p):
        ''' statement : empty
                      | expression_statement statement
                      | if_statement statement
                      
        '''
        stats = []
        i = 1
        while i < len(p):
            if isinstance(p[i],list):
                stats.extend(p[i])
            elif p[i]:
                stats.append(p[i])
            i += 1
        p[0] = stats
        #print 'LINE LINE YEAH:' + str(p.lexer.lexer.lineno)

    def p_expression_statement(self,p):
        ''' expression_statement : assignment_statement SEMI
                                 | func_call SEMI
                                 | declarator SEMI
                                 | ret SEMI
        '''
        p[0] = p[1]

    def p_assignment_statement(self,p):
        ''' assignment_statement : id EQUALS expression
        '''
        p[0] = Assignment(p[2],p[1],p[3],coord=p[1].coord)

    def p_expression(self,p):
        ''' expression : func_call
                       | unary_expression
                       | binary_expression
                       | cond_expression
        '''
        #print 'p_expression'
        p[0] = p[1]

    def p_binary_expression(self,p):
        ''' binary_expression : unary_expression bin_op unary_expression
                              | unary_expression bin_op binary_expression
                              | binary_expression bin_op binary_expression
                              | LPAREN unary_expression bin_op unary_expression RPAREN
                              | LPAREN unary_expression bin_op binary_expression RPAREN
                              | LPAREN binary_expression bin_op binary_expression RPAREN
                              
        '''
        #print 'p_binary_expression'
        start = 1
        if len(p) > 4:
            start += 1
        p[0] = BinaryOp(p[start+1],p[start],p[start+2],coord=p[start].coord)

    def p_unary_expression(self,p):
        ''' unary_expression : id
                             | int_const
                             | func_call
        '''
        p[0] = p[1]
        
    def p_bin_op(self,p):
        ''' bin_op : PLUS
                   | MINUS
                   | MULTI
                   | DIV
        '''
        p[0] = p[1]
        
    def p_cond_expression(self,p):
        ''' cond_expression : unary_expression GT unary_expression
                            | unary_expression LT unary_expression
                            | unary_expression EQ unary_expression
                            | LPAREN unary_expression GT unary_expression RPAREN
                            | LPAREN unary_expression LT unary_expression RPAREN
                            | LPAREN unary_expression EQ unary_expression RPAREN
                            | cond_expression OR cond_expression
                            | NOT cond_expression
                            | LPAREN cond_expression OR cond_expression RPAREN
                            | NOT LPAREN cond_expression RPAREN
        '''
        
        if len(p) == 3:
            p[0] = BinaryOp(p[1],p[2],None,coord=p[1].coord)
        elif len(p) == 5:
            p[0] = BinaryOp(p[1],p[3],None,coord=p[1].coord)
        else:
            start = 1
            if len(p) == 6:
                start += 1
            p[0] = BinaryOp(p[start+1],p[start],p[start+2],coord=p[start].coord)
        
        
    def p_if_statement(self,p):
        ''' if_statement : IF LPAREN cond_expression RPAREN LBRACE statement RBRACE
        '''
        p[0] = If(p[3],p[6],None,coord=self._coord(p.lexer.lexer.lineno))
        #print 'IF:' + str(p.lexer.lexer.lineno)

    def p_func_call(self,p):
        ''' func_call : ID LPAREN arg_list RPAREN
        '''
        #print 'p_func_call'
        p[0] = FuncCall(p[1],p[3],coord=self._coord(p.lexer.lexer.lineno))

    def p_arg_list_1(self,p):
        ''' arg_list : empty
        '''
        #print 'p_arg_list_1'
        p[0] = []

    def p_arg_list_2(self,p):
        ''' arg_list : int_const
                     | id
                     | str_const
                     | str_const COMMA arg_list
                     | int_const COMMA arg_list
                     | id COMMA arg_list
        '''
        #print 'p_arg_list_2'
        arg_list = []
        i = 1
        while i < len(p):
            if type(p[i]) is list:
                arg_list.extend(p[i])
            else:
                arg_list.append(p[i])
            i += 2
        p[0] = arg_list
    
    def p_int_const(self,p):
        ''' int_const : ICONST
        '''
        p[0] = IntConstant(None,p[1],coord=self._coord(p.lexer.lexer.lineno))
    
    def p_str_const(self,p):
        ''' str_const : SCONST
        '''
        p[0] = StringConstant(Node,p[1],coord=self._coord(p.lexer.lexer.lineno))
    
    def p_id(self,p):
        '''
            id : ID
        '''
        p[0] = ID(p[1],coord=self._coord(p.lexer.lexer.lineno))
        #print 'ID:' + str(p.lexer.lexer.lineno)
        
    def p_function_declaration(self,p):
        ''' function_declaration : func_decl SEMI
        '''
        p[0] = p[1]
        #print 'Func Declaration:' + str(p.lexer.lexer.lineno)

    def p_func_decl(self,p):
        '''
            func_decl : TYPEID ID LPAREN param_list RPAREN
        '''
        #print "p_func_decl"
        p[0] = FuncDecl(p[2],p[1],p[4],coord=self._coord(p.lexer.lexer.lineno))

    def p_declarator(self,p):
        '''
            declarator : TYPEID ID
        '''
        #print "p_declarator"
        #print str(p[1]) +':' + str(p[2])
        decl_node = Decl(p[1],p[2],coord=self._coord(p.lexer.lexer.lineno))
        #print str(decl_node)
        p[0] = decl_node
        
    #Empty param list
    def p_param_list_1(self,p):
        '''
            param_list : empty
        '''
        #print 'p_param_list_1'
        p[0] = DeclList([])
        
    def p_param_list_2(self,p):
        '''
            param_list : declarator
                       | declarator COMMA param_list
        '''
        #print 'p_param_list_2'
        decls = []
        i = 1
        while i < len(p):
            if type(p[i]) is DeclList:
                decls.extend(p[i].decls)
            else:
                decls.append(p[i])
            #print str(p[i])
            i += 2
        decl_list = DeclList(decls,coord=p[1].coord)
        #print str(decl_list)
        p[0] = decl_list
    
    def p_ret(self,p):
        '''
            ret : RET LPAREN expression RPAREN
        '''
        p[0] = Return(p[3],coord=p[3].coord)

    def p_empty(self,p):
        'empty : '
        p[0] = None

    def p_error(self,p):
        print self.TAG + 'Error occured during parsing:' + str(p)
