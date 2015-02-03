import ply.lex as lex
from ply.lex import TOKEN

class MyOwnLexer(object):
    def __init__(self,filename='N/A'):
    
        self.filename = filename

        # Keeps track of the last token returned from self.token()
        self.last_token = None

    def build(self, **kwargs):
        """ Builds the lexer from the specification. Must be
            called after the lexer object is created.

            This method exists separately, because the PLY
            manual warns against calling lex.lex inside
            __init__
        """
        self.lexer = lex.lex(object=self, **kwargs)

    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    def find_tok_column(self, token):
        """ Find the column of the token in its line.
        """
        last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
        return token.lexpos - last_cr

    ######################--   PRIVATE   --######################

    ##
    ## Internal auxiliary methods
    ##
    def _error(self, msg, token):
        location = self._make_tok_location(token)
        self.error_func(msg, location[0], location[1])
        self.lexer.skip(1)

    def _make_tok_location(self, token):
        return (token.lineno, self.find_tok_column(token))

    reserved = {
        'if' : 'IF',
        'taint' : 'TYPEID',
        'untaint' : 'TYPEID',
        'return' : 'RET'
    }

                
    tokens = list(set(reserved.values())) + [
        # Literals (identifier, types , integer constant, string constant)
        'ID', 'ICONST', 'SCONST',
        
        # Operators (+,-,|,~, <, >, ==)
        'PLUS', 'MINUS', 'MULTI','DIV','OR', 'NOT', 'LT', 'GT', 'EQ',
        
        # Assignment (=)
        'EQUALS',

        
        # Delimeters ( ) ,{ } , ;
        'LPAREN', 'RPAREN',
        'LBRACE', 'RBRACE',
        'COMMA', 'SEMI',
    ]


                
    t_ignore = ' \t'

    # Operators
    t_PLUS             = r'\+'
    t_MINUS            = r'-'
    t_MULTI            = r'\*'
    t_DIV              = r'/'
    t_OR               = r'\|'
    t_NOT              = r'~'
    t_LT               = r'<'
    t_GT               = r'>'
    t_EQ               = r'=='

    # Assignment operators

    t_EQUALS           = r'='


    # Delimeters
    t_LPAREN           = r'\('
    t_RPAREN           = r'\)'
    t_LBRACE           = r'\{'
    t_RBRACE           = r'\}'
    t_COMMA            = r','
    t_SEMI             = r';'



    #t_KEYWORD          = r'if'

    # Integer literal
    t_ICONST = r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'


    # String literal
    t_SCONST = r'\"([^\\\n]|(\\.))*?\"'

    def t_ID(self,t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        t.type = self.reserved.get(t.value, "ID")
        #print 'ID_LEXER:' + str(t.lexer.lineno)
        return t

    def t_error(self,t):
        print "Unrecognized token:" + str(t)
        return t
   
    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')
        #print 'INLEXER:' + str(t.lexer.lineno)
        
