import ast

from nornir.core.filter import F

class CleansingNodeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.SAFE_FX = {}
        self.SAFE_NODES = set(())
        self.nornir_locals = {}

    def generic_visit(self, node):
        if type(node) not in self.SAFE_NODES:
            raise Exception("%s not in SAFE_NODES" % type(node))
        super(CleansingNodeVisitor, self).generic_visit(node)

    def visit_Call(self, call):
        if call.func.id not in self.SAFE_FX:
            raise Exception("Unknown function: %s" % call.func.id)

    def safe_eval(self, eval_str):
        tree = ast.parse(eval_str, mode='eval')
        self.visit(tree)
        compiled = compile(tree, eval_str, "eval")
        return(eval(compiled, self.SAFE_FX, self.nornir_locals))

class InventoryVisitor(CleansingNodeVisitor):

    def __init__(self):

        super(InventoryVisitor, self).__init__()
        self.SAFE_FX = {
            'F': F,
        }
        self.SAFE_NODES = set(
            (
                ast.BitAnd,
                ast.BitOr,
                ast.BinOp,
                ast.Expression,
            )
        )

class TestVisitor(CleansingNodeVisitor):

    def __init__(self, nornir_locals):

        super(TestVisitor, self).__init__()
        self.nornir_locals = nornir_locals
        self.SAFE_NODES = set(
            (
                #ast.BitAnd,
                #ast.BitOr,
                #ast.Add,
                #ast.Assign,
                #ast.BinOp,
                ast.Compare,
                #ast.Dict,
                #ast.Div,
                ast.Expression,
                ast.Subscript,
                ast.Attribute,
                ast.Constant,
                #ast.List,
                ast.Load,
                ast.Index,
                #ast.Mult,
                #ast.Num,
                ast.Name,
                #ast.Str,
                #ast.Sub,
                #ast.USub,
                #ast.Tuple,
                #ast.UnaryOp,
                ast.Eq
            )
        )