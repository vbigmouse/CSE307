# -----------------------------------------------------------------------------
# main.py
#
# Hung-Ruey Chen 109971346
# -----------------------------------------------------------------------------

import sys, os
import ply.lex as lex
import ply.yacc as yacc
from token_def import *

# Build the lexer
def main():
    log.debug(sys.argv[1])
    sys.stderr = open(os.devnull, 'w')
    
    # lex.lex(debug=True)
    lex.lex()
    yacc.yacc()

    sys.stderr = sys.__stderr__

    r = open(sys.argv[1])
    code = ""
    for line in r:
        code += line.strip() + "\n"
    logging.debug(code)
    try:
        lex.input(code)
        while True:
            token = lex.token()
            if not token: break
            logging.debug(token)

        # ast = yacc.parse(code, debug=True)
        ast = yacc.parse(code)
        ast.execute()
    except Exception as e:
        logging.debug(e)
    r.close()

if __name__ == '__main__':
    main()