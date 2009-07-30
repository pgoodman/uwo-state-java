
# ----------------------------------------------------------------------
# StateJava: lexer.py
#
# Copyright (C) 2009, 
# Peter Goodman,
# All rights reserved.
#
# PLY Lex lexer for the State Java language.
#
# ----------------------------------------------------------------------

# reserved words / identifier handling
reserved = {
   'if' : 'IF',
   'else if' : 'ELSEIF',
   'elseif' : 'ELSEIF',
   'else' : 'ELSE',
   'while' : 'WHILE',
   'do' : 'DO',
   'for' : 'FOR',
   'default' : 'DEFAULT',
   'case' : 'CASE',
   'switch' : 'SWITCH',
   'return' : 'RETURN',
   'continue' : 'CONTINUE',
   'break' : 'BREAK',
   'import' : 'IMPORT',
   'static' : 'DEF_MODIFIER',
   'public' : 'DEF_MODIFIER',
   'final' : 'DEF_MODIFIER',
   'protected' : 'DEF_MODIFIER',
  #'abstract' : 'DEF_MODIFIER',
   'private' : 'DEF_MODIFIER',
   'class' : 'CLASS',
   'interface' : 'INTERFACE',
   'extends' : 'EXTENDS',
   'implements' : 'IMPLEMENTS',
   'new' : 'NEW',
   'states' : 'STATES',
   'package' : 'PACKAGE',
}

# tokens
tokens = (
    'ID',
    'LT',
    'GT',
    'LBRACE',
    'RBRACE',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'NUMBER',
    'STRING',
    'CHAR',
    'COMMENT',
    'STATE_TRANS',
    'COMMA',
    'QUESTION_MARK',
    'PERIOD',
    'ELLIPSIS',
    'ADD',
    'SUB',
    'MUL',
    'DIV',
    'MOD',
    'COLON',
    'SEMICOLON',
    'EQUALS',
    'NOT_EQUALS',
    'LT_EQUALS',
    'GT_EQUALS',
    'STATE',
    'WHITE_SPACE',
    'NEWLINE',
) + tuple(set(reserved.values()))

# lexemes
t_STATE         = r':[a-zA-Z0-9_]+'
t_LT            = r'\<'
t_GT            = r'\>'
t_LBRACE        = r'\{'
t_RBRACE        = r'\}'
t_LPAREN        = r'\('
t_RPAREN        = r'\)'
t_LBRACKET      = r'\['
t_RBRACKET      = r'\]'
t_NUMBER        = r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'
t_STATE_TRANS   = r'->'
t_STRING        = r'\"([^\\\n]|(\\.))*?\"'
t_CHAR          = r'\'([^\\\n]|(\\.))*?\''
t_COMMA         = r','
t_QUESTION_MARK = r'\?'
t_PERIOD        = r'\.'
t_ELLIPSIS      = r'\.\.\.'
t_COLON         = r':'
t_SEMICOLON     = r';'
t_ADD           = r'\+'
t_SUB           = r'-'
t_MUL           = r'\*'
t_DIV           = r'/'
t_MOD           = r'%'
t_EQUALS        = r'='
t_NOT_EQUALS    = r'!='
t_LT_EQUALS     = r'<='
t_GT_EQUALS     = r'>='

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# ignored chars
t_ignore_WHITE_SPACE = r"[ \t\r]+"
t_ignore_COMMENT = r'/\*(.|\n)*?\*/'

# special
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print "Scanner Error: illegal character '%s'." % t.value[0]
    t.lexer.skip(1)

# build
if __name__ == '__main__':
    import ply.lex as lex
    lexer = lex.lex()
    lexer.input(
    """
    class Moo {
        private int bar() { }
    }
    """
    )
    for tok in lexer:
        #pass
        print tok