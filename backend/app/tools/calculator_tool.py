import ast
import operator
import re

# Heuristic, not NL-to-math reasoning — finds a literal arithmetic expression in
# the query text (e.g. "what is 1234 * 1.05?"). Most natural-language healthcare
# questions ("What is my remaining coverage percentage?") don't contain one; those
# fall through to the sql tool's actual numbers instead.
_EXPRESSION_RE = re.compile(r"-?\d+(?:\.\d+)?(?:\s*[+\-*/%]\s*-?\d+(?:\.\d+)?)+")


def extract_expression(text: str) -> str | None:
    match = _EXPRESSION_RE.search(text)
    return match.group(0) if match else None

# AST-based, not eval() — only these node/operator types are ever evaluated, so
# there's no path to arbitrary code execution (imports, attribute access, calls
# to anything but the whitelisted functions, etc. all raise CalculatorError).
_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
}


class CalculatorError(ValueError):
    pass


def _eval_node(node: ast.AST):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise CalculatorError(f"Unsupported constant: {node.value!r}")
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCTIONS:
        args = [_eval_node(arg) for arg in node.args]
        return _FUNCTIONS[node.func.id](*args)
    raise CalculatorError(f"Unsupported expression: {ast.dump(node)}")


def evaluate(expression: str) -> float:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise CalculatorError(f"Invalid expression: {exc}") from exc
    try:
        return _eval_node(tree.body)
    except ZeroDivisionError as exc:
        raise CalculatorError("Division by zero") from exc
