import re
from sympy import sympify, diff, integrate, solve, limit, simplify, trigsimp

def _format(expr):
    expr = simplify(expr)
    expr = trigsimp(expr)
    return str(expr).replace("**", "^")

def _get_variable(expr):
    symbols = list(expr.free_symbols)
    return symbols[0] if symbols else None

def _clean(query, keyword):
    # removes keyword and filler words like "of"
    return query.replace(keyword, "").replace("of", "").strip()

def solve_math_query(query):
    query = query.lower().strip()

    try:
        # DERIVATIVE
        if "differentiate" in query or "derivative" in query:
            expr_text = _clean(query, "differentiate")
            expr_text = _clean(expr_text, "derivative")
            expr = sympify(expr_text)
            var = _get_variable(expr)
            if not var:
                return None
            result = diff(expr, var)
            return f"d/d{var} = {_format(result)}"

        # INTEGRATION
        if "integrate" in query:
            expr_text = _clean(query, "integrate")
            expr = sympify(expr_text)
            var = _get_variable(expr)
            if not var:
                return None
            result = integrate(expr, var)
            return f"∫ d{var} = {_format(result)}"

        # LIMIT
        if "limit" in query:
            # example: limit sin(x)/x as x->0
            expr_part, point_part = query.split("as")
            expr = sympify(expr_part.replace("limit", "").replace("of", ""))
            var = _get_variable(expr)
            point = sympify(point_part.split("->")[1])
            result = limit(expr, var, point)
            return f"Limit = {_format(result)}"

        # SOLVE
        if "solve" in query:
            expr_text = _clean(query, "solve")
            expr = sympify(expr_text)
            var = _get_variable(expr)
            if not var:
                return None
            sol = solve(expr, var)
            return f"{var} = {_format(sol)}"

        # SIMPLE EXPRESSION
        if re.search(r"[0-9a-z+\-*/^()]", query):
            expr = sympify(query)
            return f"Result = {_format(expr)}"

        return None

    except Exception:
        return None
