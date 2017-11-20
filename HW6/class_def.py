# -----------------------------------------------------------------------------
# main.py
# define class of Abstract Syntax Tree Nodes
# Hung-Ruey Chen 109971346
# -----------------------------------------------------------------------------

import logging
fmt = "[%(levelname)s]%(funcName)s():%(lineno)i: %(message)s "
logging.basicConfig(level=logging.ERROR, format=fmt)
# logging.basicConfig(level=logging.DEBUG, format=fmt)
log = logging.getLogger(__name__)


class StackFrame:
    def __init__(self):
        self.stack = [{}]
    
    def push(self):
        self.stack.append({})
    
    def pop(self):
        self.stack.pop()

    def peek(self):
        return self.stack[len(self.stack) - 1]

    def lookup(self, name):
        logging.debug(name)
        for frame in reversed(self.stack):
            logging.debug(frame)
            if name in frame:
                return frame[name]
        return None

    def assign(self, name, value):
        logging.debug(str(name) + '=' + str(value))
        self.stack[len(self.stack) - 1][name] = value

    def size(self):
        return len(self.stack)

    def create_frame(self, args_name, args_value):
        self.push()
        logging.debug(args_name)
        logging.debug(args_value)
        for pair in list(zip(args_name, args_value)):
            self.assign(pair[0], pair[1])

    def remove_frame(self):
        logging.debug('remove frame')
        self.pop()

names = StackFrame()

class Node:
    def __init__(self):
        pass

    def evaluate(self):
        return 0

    def execute(self):
        return 0

class ProgramNode(Node):
    def __init__(self, blocks):
        self.blks = blocks

    def execute(self):
        self.blks.execute()

class FunctionNode(Node):
    def __init__(self, name, args, block):
        self.name = name
        self.args_name = args
        self.blk = block
        global names
        names.assign(self.name, self) 
    
    def execute(self, args_value):
        global names
        names.create_frame(self.args_name, list(args_value))
        result = self.blk.execute()
        names.remove_frame()
        return result


class BlocksNode(Node):
    def __init__(self, block):
        self.blks_head = block
        self.blks_tail = block
    
    def AddBlk(self, block):
        self.blks_tail.next_blk = block
        self.blks_tail = block
    
    def execute(self):
        exe_blk = self.blks_head
        while exe_blk:
            logging.debug(exe_blk)
            result = exe_blk.execute()
            exe_blk = exe_blk.next_blk
        logging.debug(result)
        return result

class BlockNode(Node):
    def __init__(self, smts, start_ln=0, end_ln=0):
        self.start = start_ln
        self.end = end_ln
        self.smts = smts
        self.next_blk = None
        
    def execute(self):
        result = self.smts.execute()
        logging.debug(result)
        return result

class EmptyBlk(Node):
    def __init__(self, start_ln=0, end_ln=0):
        self.start = start_ln
        self.end = end_ln
        self.next_blk = None

    def execute(self):
        pass

class SmtsNode(Node):
    def __init__(self, smt):
        self.smts_head = smt
        self.smts_tail = smt

    def AddSmt(self, smt):
        self.smts_tail.next_smt = smt
        self.smts_tail = smt

    def execute(self):
        exe_smt = self.smts_head
        while exe_smt:
            logging.debug(exe_smt)
            result = exe_smt.execute()
            if result != None:
                break
            logging.debug(exe_smt)
            exe_smt = exe_smt.next_smt
        logging.debug(result)
        return result

class SmtNode(Node):
    def __init__(self):
        self.next_smt = None

class BlkSmt(SmtNode):
    def __init__(self, blk):
        SmtNode.__init__(self)
        self.blk = blk

    def execute(self):
        self.blk.execute()

class AssignSmt(SmtNode):
    def __init__(self, name, exp):
        SmtNode.__init__(self)
        self.name = name
        self.exp = exp
    
    def execute(self):
        logging.debug(str(self.name) + str(self.exp))
        global names
        names.assign(self.name, self.exp.evaluate())

class ListAssignSmt(SmtNode):
    def __init__(self, indexp, exp):
        SmtNode.__init__(self)
        self.indexp = indexp
        self.exp = exp
    
    def execute(self):
        logging.debug(self.indexp.list_exp.evaluate())
        self.indexp.list_exp.evaluate()[self.indexp.ind.evaluate()] = self.exp.evaluate()

class EmptySmt(SmtNode):
    def __init__(self):
        SmtNode.__init__(self)
    
    def execute(self):
        pass

# class ExpSmt(SmtNode):
#     def __init__(self, exp):
#         SmtNode.__init__(self)
#         self.exp = exp
    
#     def evaluate(self):
#         return self.exp.evaluate()

class ReturnSmt(SmtNode):
    def __init__(self, exp):
        SmtNode.__init__(self)
        self.exp = exp

    def execute(self):
        logging.debug(self.exp.evaluate())
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
            result = self.ifblock.execute()
        elif self.elseblock:
            logging.debug(self.elseblock)
            result = self.elseblock.execute()
        return result

class ElseSmt(SmtNode):
    def __init__(self, elseblock):
        SmtNode.__init__(self)
        self.elseblock = elseblock

    def execute(self):
        logging.debug(self.elseblock)
        if self.elseblock:
            result = self.elseblock.execute()
            return result

class WhileSmt(SmtNode):
    def __init__(self, exp, block):
        SmtNode.__init__(self)
        self.exp = exp
        self.block = block
    
    def execute(self):
        logging.debug(self.exp)
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
            print("SYNTAX ERROR")
            raise TypeError

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
            print("SYNTAX ERROR")
            raise TypeError

class IDExp(ExpNode):
    def __init__(self, id):
        ExpNode.__init__(self)
        self.id = id
        self.type = type(self)

    def evaluate(self):
        logging.debug(self.id)
        global names
        result = names.lookup(self.id)
        if result != None:
            return result 
        else:
            logging.debug("Variable Not Defined")
            print("SEMANTIC ERROR")
            raise ValueError 

class FuncExp(ExpNode):
    def __init__(self, name, args_value):
        ExpNode.__init__(self)
        self.name = name
        self.args_value = args_value

    def evaluate(self):
        logging.debug(str(self.name) + '(' + str(self.args_value) +')')
        global names
        func = names.lookup(self.name)
        if func != None:
            if isinstance(func, FunctionNode):
                result = func.execute(self.args_value.evaluate())
                if result != None:
                    return result
                else:
                    logging.debug("No Return Value")
            else:
                logging.debug("Not a Function")
        else:
            logging.debug("Function Not Defined")
        print("SEMANTIC ERROR")
        raise ValueError

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
            logging.debug(exe_exp.evaluate())
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
        logging.debug(self.value)
        return self.value

class ListNode(Node):
    def __init__(self, head):
        self.head = head
        logging.debug("init list" + str(head))

    def evaluate(self):
        logging.debug(self.head)
        return [] if isinstance(self.head.exps_head, EmptyExp) else list(self.head.evaluate())

class IndexNode(Node):
    def __init__(self, exp):
        self.exp = exp

    def evaluate(self):
        return self.exp.evaluate()

class ListIndex(Node):
    def __init__(self, list_exp, ind):
        self.list_exp = list_exp
        self.ind = ind

    def evaluate(self):
        logging.debug(self.list_exp)
        index = self.ind.evaluate()
        listexp = self.list_exp.evaluate()
        if index < len(listexp):
            return self.list_exp.evaluate()[self.ind.evaluate()]
        else:
            logging.debug("Index Out of Range")
            print("SEMANTIC ERROR")
            raise ValueError
