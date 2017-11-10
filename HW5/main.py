# -----------------------------------------------------------------------------
# main.py
#
# Hung-Ruey Chen 109971346
# -----------------------------------------------------------------------------

import sys
import ply.lex as lex
import ply.yacc as yacc
from class_def import *

reserved = {
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'print' : 'PRINT'
}

tokens = (
    [
        # 'NAME',
    'NUMBER','STRING',
    'PLUS','MINUS','TIMES','DIVIDE','EQUAL','MOD',
    'PLUSEQ','MINUSEQ','TIMESEQ','DIVIDEEQ','MODEQ',
    'GREATER','SMALLER','AND','OR','IN','NOT',
    'LPAREN','RPAREN','QUOTA','DQUOTA','LBRACK','RBRACK','LBRACE','RBRACE',
    'EEQUAL','GEQUAL','LEQUAL','NEQUAL','TTIMES','DDIVIDE',
    'DOT','COMMA','SEMCOLON','ID']
    + list(reserved.values()) )

# Tokens

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_MOD     = r'%'
t_PLUSEQ  = r'\+='
t_MINUSEQ = r'-='
t_TIMESEQ = r'\*='
t_DIVIDEEQ = r'/='
t_MODEQ   = r'%='
t_EQUAL   = r'='
t_GREATER = r'>'
t_SMALLER = r'<'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACK  = r'\['
t_RBRACK  = r'\]'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_COMMA   = r','
t_QUOTA   = r'\''
t_EEQUAL  = r'=='
t_GEQUAL  = r'>='
t_LEQUAL  = r'<='
t_NEQUAL  = r'<>'
t_TTIMES  = r'\*\*'
t_DDIVIDE = r'//'
t_DOT     = r'\.'
t_SEMCOLON = r'\;'
# t_DQUOTA  = r'\"'
# t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_STRING(t):
    r'([\"])(.*?\2)'
    t.value = StringExp(t.value[1:-1])
    return t

def t_NUMBER(t): 
    r'\d+(\.(\d*))?'
    try:
        t.value = NumberExp(t.value)
    except ValueError:
        print("Value too large %f", t.value)
        t.value = 0
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

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
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
# names = { }

def p_block(t):
    '''
    block : LBRACE smts RBRACE
    '''
    t[0] = BlockNode(t[2], t.lineno(1), t.lineno(3))

def p_smts(t):
    '''
    smts : smt
         | smts smt
    '''
    if len(t) == 2:
        logging.debug(t[1])
        t[0] = SmtsNode(t[1])
    else:
        logging.debug(t[2])
        t[1].AddSmt(t[2])
        t[0] = t[1]

def p_print_smt(t):
    '''
    smt : PRINT LPAREN exp RPAREN SEMCOLON
    '''
    t[0] = PrintSmt(t[3])

def p_exp_smt(t):
    '''
    smt : exp SEMCOLON
    '''
    t[0] = ExpSmt(t[1])

def p_assign_smt(t):
    '''
    smt : ID EQUAL exp SEMCOLON
    '''
    t[0] = AssignSmt(t[1], t[3])

def p_list_assign_smt(t):
    '''
    smt : ID LBRACK exp RBRACK EQUAL exp SEMCOLON
    '''
    t[0] = ListAssignSmt(t[1], t[3], t[6])

def p_binaryop_assign_smt(t):
    '''
    smt : ID PLUSEQ exp SEMCOLON
        | ID MINUSEQ exp SEMCOLON
        | ID TIMESEQ exp SEMCOLON
        | ID DIVIDEEQ exp SEMCOLON
        | ID MODEQ exp SEMCOLON
    '''
    logging.debug(t[2][0])
    t[0] = AssignSmt(t[1], BinaryOpExp(t[2][0], IDExp(t[1]), t[3]))

def p_condition_smt(t):
    '''
    smt : ifsmt
        | whilesmt
    '''
    t[0] = t[1]

def p_if_smt(t):
    '''
    ifsmt : IF LPAREN exp RPAREN block elsesmt
          | IF LPAREN exp RPAREN smt elsesmt 
    '''
    t[0] = IfSmt(t[3], t[5], t[6])

def p_else_smt(t):
    '''
    elsesmt : ELSE block
            | ELSE smt
            | ELSE ifsmt
            | empty
    '''
    if len(t) == 3:
        t[0] = ElseSmt(t[2])
    else:
        t[0] = EmptyExp()

def p_while_smt(t):
    '''
    whilesmt : WHILE LPAREN exp RPAREN block
             | WHILE LPAREN exp RPAREN smt
    '''
    t[0] = WhileSmt(t[3], t[5])

def p_id_exp(t):
    '''
    exp : ID
    '''
    t[0] = IDExp(t[1])

def p_binaryop_exp(t):
    '''
    exp : exp PLUS exp
        | exp MINUS exp
        | exp TIMES exp
        | exp DIVIDE exp
        | exp MOD exp
        | exp TTIMES exp
        | exp DDIVIDE exp
        | exp GREATER exp
        | exp SMALLER exp
        | exp EEQUAL exp
        | exp GEQUAL exp
        | exp LEQUAL exp
        | exp NEQUAL exp
        | exp AND exp
        | exp OR exp
    '''
    t[0] = BinaryOpExp(t[2], t[1], t[3])

def p_uniary_exp(t):
    '''
    exp : MINUS exp
        | NOT exp
    '''
    t[0] = UiaryOpExp(t[2], t[1])  


def p_single_exp(t):
    ''' 
    exp : NUMBER
        | STRING
        | list
        | index
    '''
    t[0] = SingleExp(t[1]) 

def p_parent_exp(t):
    '''
    exp : LPAREN exp RPAREN
    '''
    t[0] = t[2]

def p_exps(t):
    '''
    exps : empty
         | exp
         | exps COMMA exp
    '''
    logging.debug(t[1])
    if len(t) == 2:
        t[0] = ExpsExp(t[1])
    else:
        t[1].AddExp(t[3])
        t[0] = t[1]

def p_list(t):
    '''
    list : LBRACK exps RBRACK
    '''
    t[0] = ListNode(t[2])

def p_index(t):
    '''
    index : exp LBRACK exp RBRACK
    '''
    t[0] = ListIndex(t[1], t[3])

def p_empty(t):
    'empty :'
    t[0] = EmptyExp()

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
    code = ""
    for line in r:
        code += line.strip()
    try:
        lex.input(code)
        while True:
            token = lex.token()
            if not token: break
            logging.debug(token)

        # yacc.parse(code)
        ast = yacc.parse(code, debug=True)
        # ast = yacc.parse(code)
        ast.execute()
    except Exception as e:
        logging.error(e)
    r.close()

if __name__ == '__main__':
    main()