# -----------------------------------------------------------------------------
# main.py
#
# Hung-Ruey Chen 109971346
# -----------------------------------------------------------------------------

import logging
fmt = "[%(levelname)s]%(funcName)s():%(lineno)i: %(message)s "
# logging.basicConfig(level=logging.ERROR, format=fmt)
logging.basicConfig(level=logging.DEBUG, format=fmt)
log = logging.getLogger(__name__)


class Node:
    def __init__(self):
        pass

    def evaluate(self):
        return 0

    def execute(self):
        return 0

names = {}

class BlockNode(Node):
    def __init__(self, smts, start_ln=0, end_ln=0):
        self.start = start_ln
        self.end = end_ln
        self.smts = smts
        
    def execute(self):
        exe_smt = self.smts.smts_head
        while exe_smt:
            logging.debug(exe_smt)
            exe_smt.execute()
            exe_smt = exe_smt.next_smt

class SmtsNode(Node):
    def __init__(self, smt):
        self.smts_head = smt
        self.smts_tail = smt

    def AddSmt(self, smt):
        self.smts_tail.next_smt = smt
        self.smts_tail = smt

class SmtNode(Node):
    def __init__(self):
        self.next_smt = None

class AssignSmt(SmtNode):
    def __init__(self, name, exp):
        SmtNode.__init__(self)
        self.name = name
        self.exp = exp
    
    def execute(self):
        logging.debug(str(self.name) + str(self.exp))
        global names
        names[self.name] = self.exp.evaluate()

class ListAssignSmt(SmtNode):
    def __init__(self, id, indexp, exp):
        SmtNode.__init__(self)
        self.id = id
        self.indexp = indexp
        self.exp = exp
    
    def execute(self):
        global names
        logging.debug(self.indexp.evaluate())
        names[self.id][self.indexp.evaluate()] = self.exp.evaluate()


class ExpSmt(SmtNode):
    def __init__(self, exp):
        SmtNode.__init__(self)
        self.exp = exp
    
    def evaluate(self):
        return self.exp.evaluate()

class PrintSmt(SmtNode):
    def __init__(self, exp):
        SmtNode.__init__(self)
        self.exp = exp

    def execute(self):
        logging.debug(self.exp)
        print(self.exp.evaluate())

class IfSmt(SmtNode):
    def __init__(self, ifexp, ifblock, elseblock=None):
        SmtNode.__init__(self)
        self.exp = ifexp
        self.ifblock = ifblock
        self.elseblock = elseblock
    
    def execute(self):
        logging.debug(self.exp)
        if self.exp.evaluate():
            logging.debug(self.ifblock)
            self.ifblock.execute()
        elif self.elseblock:
            logging.debug(self.elseblock)
            self.elseblock.execute()

class ElseSmt(SmtNode):
    def __init__(self, elseblock):
        SmtNode.__init__(self)
        self.elseblock = elseblock

    def execute(self):
        logging.debug(self.elseblock)
        if self.elseblock:
            self.elseblock.execute()

class WhileSmt(SmtNode):
    def __init__(self, exp, block):
        SmtNode.__init__(self)
        self.exp = exp
        self.block = block
    
    def execute(self):
        while(self.exp.evaluate()):
            logging.debug(self.block)
            self.block.execute()

class ExpNode(Node):
    def __init__(self):
        self.next_exp = None

class SingleExp(ExpNode):
    def __init__(self, exp):
        ExpNode.__init__(self)
        self.exp = exp
        self.type = type(exp)
    
    def evaluate(self):
        return self.exp.evaluate()

class BinaryOpExp(ExpNode):
    def __init__(self, op, exp1, exp2):
        ExpNode.__init__(self)
        self.exp1 = exp1
        self.exp2 = exp2
        self.op = op
        self.type = type(self)
    
    def evaluate(self):
        logging.debug(str(self.exp1) + str(self.op) + str(self.exp2))
        if self.op == '+':
            return self.exp1.evaluate() + self.exp2.evaluate()
        elif self.op =='-':
            return self.exp1.evaluate() - self.exp2.evaluate()
        elif self.op =='*':
            return self.exp1.evaluate() * self.exp2.evaluate()
        elif self.op =='/':
            return self.exp1.evaluate() / self.exp2.evaluate()
        elif self.op =='%':
            return self.exp1.evaluate() % self.exp2.evaluate()
        elif self.op =='**':
            return self.exp1.evaluate() ** self.exp2.evaluate()
        elif self.op =='//':
            return self.exp1.evaluate() // self.exp2.evaluate()
        elif self.op =='>':
            return 1 if self.exp1.evaluate() > self.exp2.evaluate() else 0
        elif self.op =='<':
            return 1 if self.exp1.evaluate() < self.exp2.evaluate() else 0
        elif self.op =='==':
            return 1 if self.exp1.evaluate() == self.exp2.evaluate() else 0
        elif self.op =='>=':
            return 1 if self.exp1.evaluate() >= self.exp2.evaluate() else 0
        elif self.op =='<=':
            return 1 if self.exp1.evaluate() <= self.exp2.evaluate() else 0
        elif self.op =='<>':
            return 1 if self.exp1.evaluate() != self.exp2.evaluate() else 0
        elif self.op =='and':
            return 1 if self.exp1.evaluate() and self.exp2.evaluate() else 0
        elif self.op =='or':
            return 1 if self.exp1.evaluate() or self.exp2.evaluate() else 0
        else:
            logging.error("Syntax Error")

class UniaryOpExp(ExpNode):
    def __init__(self, op, exp):
        ExpNode.__init__(self)
        self.exp = exp
        self.op = op
        self.type = type(exp)
    
    def evaluate(self):
        if self.op =='-':
            return - self.exp.evaluate()
        elif self.op == 'not':
            return not self.exp.evaluate()
        else:
            logging.error("Syntax Error")

class IDExp(ExpNode):
    def __init__(self, id):
        ExpNode.__init__(self)
        self.id = id
        self.type = type(self)

    def evaluate(self):
        logging.debug(self.id)
        global names
        return names[self.id]

class EmptyExp(ExpNode):
    def __init__(self):
        ExpNode.__init__(self)
        self.type = type(self)
    
    def evaluate(self):
        return None

class ExpsExp(ExpNode):
    def __init__(self, exp):
        ExpNode.__init__(self)
        self.exps_head = exp
        self.exps_tail = exp
        self.exps_len = 1
        self.type = type(self)

    def AddExp(self, exp):
        self.exps_tail.next_exp = exp
        self.exps_tail = exp
        self.exps_len = self.exps_len + 1
    
    def evaluate(self):
        exe_exp = self.exps_head
        while exe_exp:
            logging.debug(exe_exp)
            yield exe_exp.evaluate()
            exe_exp = exe_exp.next_exp


class NumberExp(ExpNode):
    def __init__(self, num):
        ExpNode.__init__(self)
        if('.' in num):
            self.value = float(num)
        else:
            self.value = int(num)

    def evaluate(self):
        return self.value

class StringExp(ExpNode):
    def __init__(self, string):
        ExpNode.__init__(self)
        self.value = string
    
    def evaluate(self):
        return '\'' + self.value + '\''

class ListNode(Node):
    def __init__(self, head):
        self.head = head
        logging.debug("init list" + str(head))

    def evaluate(self):
        return [] if isinstance(self.head.exps_head, EmptyExp) else list(self.head.evaluate())

class ListIndex(Node):
    def __init__(self, list_exp, ind):
        self.ind = ind
        self.list_exp = list_exp

    def evaluate(self):
        return self.list_exp.evaluate()[self.ind.evaluate()]
