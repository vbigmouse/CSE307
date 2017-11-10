# -----------------------------------------------------------------------------
# stonyBrookScript.py
#
# Hung-Ruey Chen 109971346
# -----------------------------------------------------------------------------

import sys
import ply.lex as lex
import ply.yacc as yacc
import logging
fmt = "[%(levelname)s]%(funcName)s():%(lineno)i: %(message)s "
logging.basicConfig(level=logging.ERROR, format=fmt)
log = logging.getLogger(__name__)

tokens = (
    'NAME','NUMBER','STRING',
    'PLUS','MINUS','TIMES','DIVIDE','EQUALS','MOD','GREATER','SMALLER','AND','OR','IN','NOT',
    'LPAREN','RPAREN','QUOTA','DQUOTA','COMMA','LBRACK','RBRACK',
    'EEQUAL','GEQUAL','LEQUAL','NEQUAL','TTIMES','DDIVIDE','DOT',
    )

# Tokens

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_MOD     = r'%'
t_DIVIDE  = r'/'
t_EQUALS  = r'='
t_GREATER = r'>'
t_SMALLER = r'<'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACK  = r'\['
t_RBRACK  = r'\]'
t_COMMA   = r','
t_QUOTA   = r'\''
t_EEQUAL  = r'=='
t_GEQUAL  = r'>='
t_LEQUAL  = r'<='
t_NEQUAL  = r'<>'
t_TTIMES  = r'\*\*'
t_DDIVIDE = r'//'
t_DOT     = r'.'
# t_DQUOTA  = r'\"'
t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_STRING(t):
    r'([\"])(.*?\2)'
    t.value = t.value[1:-1]
    logging.debug('t_string:' + t.value)
    return t


def t_NUMBER(t): 
    r'\d+(\.(\d*))?'
    if '.' in t.value:
        try:
            t.value = float(t.value)
        except ValueError:
            print("Float value too large %f", t.value)
            t.value = 0
    else:
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %d", t.value)
            t.value = 0
        
    logging.debug('t_num'+str(t))
    return t

def t_AND(t):
    r'\band\b'
    return t

def t_OR(t):
    r'\bor\b'
    return t

def t_NOT(t):
    r'\bnot\b'
    return t

def t_IN(t):
    r'\bin\b'
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    

# Parsing rules
precedence = (
    ('left','OR'),
    ('left','AND'),
    ('left','NOT'),
    ('left','EEQUAL','GEQUAL','LEQUAL','NEQUAL','GREATER','SMALLER'),
    ('right','IN'),
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE','MOD','TTIMES','DDIVIDE'),
    )

# dictionary of names
names = { }

def p_statement_assign(t):
    'statement : NAME EQUALS expression'
    logging.debug("assign")
    names[t[1]] = t[3]

def p_statement_expr(t):
    'statement : expression'
    logging.debug("express")
    if isinstance(t[1], str):
        print("'" + t[1] + "'")
    else:
        print((t[1]))

def p_expression_in_op(t):
    '''expression : expression IN expression'''
    if isinstance(t[3], list) or isinstance(t[3], str):
        if t[2] == 'in'   : t[0] = 1 if t[1] in t[3] else 0
    #elif isinstance
    else:
       print("SEMANTIC ERROR")
       raise TypeError

def p_expression_logic_op(t):
    '''expression : expression AND expression
                  | expression OR expression'''

    if isinstance(t[1], int):
        if t[2] == 'and'   : t[0] = 0 if t[1]==0 or t[3]==0 else 1
        elif t[2] == 'or' : t[0] = 0 if t[1]==0 and t[3]==0 else 1
    else:
        print("SEMANTIC ERROR")
        raise TypeError

def p_expression_uni_op(t):
    '''expression : NOT expression'''
    if isinstance(t[2], int):
        if t[1] == 'not' : t[0] = 1 if t[2] == 0 else 0
    else:
        print("SEMANTIC ERROR")
        raise TypeError

def p_expression_long_op(t):
    '''expression : expression TTIMES expression
                  | expression GEQUAL expression
                  | expression LEQUAL expression
                  | expression EEQUAL expression
                  | expression NEQUAL expression
                  | expression DDIVIDE expression'''
    if isinstance(t[1], type(t[3])) and (isinstance(t[1], int) or isinstance(t[1], float)):
        #print(str(t[0]) +" "+str(t[1])+" "+str(t[2])+str(t[3])+" "+str(t[4]))
        if t[2] == '**'   : t[0] = t[1] ** t[3]
        elif t[2] == '//' : 
            if t[3] != 0: t[0] = t[1] // t[3] 
            else: 
                print("SEMANTIC ERROR")
                raise ValueError
        elif t[2] == '<>' : t[0] = 1 if t[1] != t[3] else 0
        elif t[2] == '>=' : t[0] = 1 if t[1] >= t[3] else 0
        elif t[2] == '<=' : t[0] = 1 if t[1] <= t[3] else 0
        elif t[2] == '==' : t[0] = 1 if t[1] == t[3] else 0
    else:
        print("SEMANTIC ERROR")
        raise TypeError

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression
                  | expression GREATER expression
                  | expression SMALLER expression'''

    logging.debug("list:'%s %s %s'" % (t[1],t[2],t[3] ))
    if isinstance(t[1], type(t[3])):
        if t[2] == '+'   : t[0] = t[1] + t[3]
        elif t[2] == '-' : t[0] = t[1] - t[3]
        elif t[2] == '*' : t[0] = t[1] * t[3]
        elif t[2] == '/' : 
            if t[3] != 0:
                t[0] = t[1] / t[3]
            else:
                print("SEMANTIC ERROR")
                raise ValueError
        elif t[2] == '%' : t[0] = t[1] % t[3]
        elif t[2] == '>' : t[0] = 1 if t[1] > t[3] else 0
        elif t[2] == '<' : t[0] = 1 if t[1] < t[3] else 0
    else:
        print("SEMANTIC ERROR")
        raise TypeError
# for string 
def p_expression_string(t):
    '''expression : STRING '''
    t[0] = t[1]

def p_list_index(t):
    '''list_index : list LBRACK expression RBRACK'''
    logging.debug("list:'%s %s %s %s'" % (t[1],t[2],t[3], t[4] ))
    try:
        ind = int(t[3])
    except ValueError:
        print("Index not valid")
    t[0] = t[1][ind]

def p_expressions(t):
    '''expressions : expression'''
    t[0] = [t[1]]

def p_expressions_list(t):
    '''expressions : expressions COMMA expression'''
    t[0] = t[1] + [t[3]]

def p_list(t):
    '''list : LBRACK expressions RBRACK
            | LBRACK RBRACK
            | list_index'''
    if len(t) > 2:
        t[0] = t[2] 
    else:
        t[0] = t[1]

def p_expression_list(t):
    '''expression : list'''
    logging.debug("list:'%s'" % str(t) )
    t[0] = t[1]

def p_list_op(t):
    '''list : list PLUS list
            | list PLUS expression'''
    if t[2] == '+'   : t[0] = t[1] + t[3]

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_expression_number(t):
    'expression : NUMBER'
    t[0] = t[1]

def p_expression_name(t):
    'expression : NAME'
    try:
        t[0] = names[t[1]]
    except LookupError:
        t[0] = 0
        raise SyntaxError

def p_error(t):
    print("SYNTAX ERROR")
    raise SyntaxError
    

# Build the lexer
def main():
    log.debug(sys.argv[1])
    # lex.lex(debug=1)
    lex.lex()
    yacc.yacc()
    r = open(sys.argv[1])
    for line in r:
        # print(line)
        try:
            yacc.parse(line)
            # yacc.parse(line, debug=True)
        except Exception as e:
            pass
    r.close()

if __name__ == '__main__':
    main()