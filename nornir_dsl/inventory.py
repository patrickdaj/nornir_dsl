from nornir_dsl.utils.safe_evals import InventoryVisitor
from nornir.core.filter import F

def get_inventory(nornir, filter_str):
    inv_parser = InventoryVisitor()
    return nornir.filter(inv_parser.safe_eval(filter_str))