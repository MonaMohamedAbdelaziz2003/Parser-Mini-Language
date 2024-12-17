import re

def space(tokens):  # rec
    if not tokens:
        return []
    if tokens[0] != ' ' and tokens[0] != '':
        return [tokens[0]] + space(tokens[1:])
    else:
        return space(tokens[1:])

# list ده االتوكنيز عادي بقطع الكود ل
def toknize(input):
  tokens = re.split(r'(\s|[=+*/()^!<>-]|==|!=|>=|<=|&&|\|\||for|if|else|;|then)', input)
  # tokens = list(filter(lambda token: token.strip(), tokens))
  tokens =space(tokens)


  return tokens

# test toknize
# print(toknize("x=(2 + 3)*4; if x>=3 then y=2 else y=6 "))


# برجع  الأولوية  بتاع كل عمليه

def get_precedence(operator):
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '**': 3, '==': 0, '!=': 0, '>': 0, '<': 0, '>=': 0, '<=': 0}
    return precedence.get(operator, 0)


# هنا بمعمل بارسر للعمليات العاديه غير الكونديشن
# للمتغيرات
def parse_primary(tokens):
    if not tokens:
        raise ValueError("Unexpected end of input in expression")

    token = tokens[0]

    match token:
        case token if token.isdigit():
            return ("Number", int(token)), tokens[1:]
        case token if token.isalpha():
            return ("Variable", token), tokens[1:]
        case "(":
            expr, remaining = parse_expression(tokens[1:])
            if remaining[0] != ')':
                raise ValueError("Expected closing parenthesis")
            return expr, remaining[1:]
        # case _:
        #     raise ValueError(f"Unexpected token: {token}")


# العمليات الحسابيه
def parse_binop(left, tokens, current_precedence=0):

    if not tokens:
        return left, tokens
    token = tokens[0]

    # هنا بشوف العمليه اللي هتحصل وبجيب الرقم اللي ع يمينه وشماله
    # وبتشك الأولوية العمليه اللي هتحصل وهل هيا من ضمن عمليات البارسر ولا لا
    match token:
        case token if token in ('+', '-', '*', '/', '**', '==', '!=', '>', '<', '>=', '<=') and get_precedence(token) >= current_precedence:
            operator = token
            tokens = tokens[1:]
            right, tokens = parse_primary(tokens)
            left = ("BinaryOp", operator, left, right)
            return parse_binop(left, tokens, current_precedence)

    return left, tokens


# بحلل المعادله اللي بعد يساوي او ال اف
def parse_expression(tokens):
    left, tokens = parse_primary(tokens)  # بتعرغ الارقام او المتغيرات عموما
    left, tokens = parse_binop(left, tokens)  # العمليات الرياضيه
    return left, tokens


# فيها يساوي statement لو ال
def parse_assignment(tokens):
    variable = tokens[0]
    tokens = tokens[2:]
    expr, tokens = parse_expression(tokens)
    return ("Assignment", variable, expr), tokens



def parse_if(tokens):
    condition, tokens = parse_expression(tokens)

    match tokens:
        case [ "then", *rest ]:
            tokens = rest
        case _:
            raise ValueError("Expected 'then' after condition")

    then_stmt, tokens = parse_statement(tokens)
    else_stmt = None

    match tokens:
        case [ "else", *rest ]:
            tokens = rest
            else_stmt, tokens = parse_statement(tokens)

    return ("If", condition, then_stmt, else_stmt), tokens



# = عبارة عن كونديشن ولا معادله طرفين فيها يساوي  statement هنا بشوف ال
def parse_statement(tokens):
    match tokens:
        case ['if', *rest]:
            tokens = rest
            return parse_if(tokens)

        case [var, '=', *rest]:
            return parse_assignment(tokens)

        case _:
            raise ValueError(f"Unexpected statement token: {tokens[0]}")

# بتشك لو مدخله اكتر من ستاتمنت
def parse_statements(tokens):
    if not tokens:
        return [], tokens

    stmt, remaining_tokens = parse_statement(tokens)

    match remaining_tokens:
        case [";", *rest]:
            remaining_tokens = rest

    rest_statements, final_tokens = parse_statements(remaining_tokens)
    return [stmt] + rest_statements, final_tokens


def parseer(tokens):
    statements, remaining_tokens = parse_statements(tokens)
    if remaining_tokens:
        raise ValueError(f"Unexpected tokens remaining: {remaining_tokens}")
    return statements


# واخيرا بقا ده اخر واحده بترجع الناتج النهائي
def evaluate_primary(node, variables):
    match node:
        case ("Number", value):
            return value
        case ("Variable", var_name):
            if var_name not in variables:
                raise ValueError(f"Undefined variable: {var_name}")
            return variables[var_name]
        case _:
            raise ValueError(f"Unexpected node type: {node[0]}")


# ده اله حاسبه بتاع اولى ابتدائي عادي
def evaluate_binop(node, variables):
    match node:
        case ("BinaryOp", operator, left_node, right_node):
            left = evaluate(left_node, variables)
            right = evaluate(right_node, variables)

            match operator:
                case "+":
                    return left + right
                case "-":
                    return left - right
                case "*":
                    return left * right
                case "/":
                    if right == 0:
                        raise ZeroDivisionError("Division by zero")
                    return left / right
                case "**":
                    return left ** right
                case "==":
                    return left == right
                case "!=":
                    return left != right
                case ">":
                    return left > right
                case "<":
                    return left < right
                case ">=":
                    return left >= right
                case "<=":
                    return left <= right
                case _:
                    raise ValueError(f"Unexpected operator: {operator}")
        case _:
            raise ValueError(f"Unexpected node type for binary operation: {node[0]}")
# def evaluate_binop(node, variables):
#     _, operator, left, right = node  #  Pure Functions
#     left_val = evaluate(left, variables)
#     right_val = evaluate(right, variables)
#     return {
#         "+": left_val + right_val,
#         "-": left_val - right_val,
#         "*": left_val * right_val,
#         # "/": left_val / right_val,
#         "==": left_val == right_val,
#         "!=": left_val != right_val,
#         "**": left_val ** right_val,
#         ">": left_val > right_val,
#         ">=": left_val >= right_val,
#         "<": left_val < right_val,
#         "<=": left_val <= right_val
#     }.get(operator, 0)


# x= 2+5 <<<= = بنحل الجزء اللي قدام
def evaluate_assignment(node, variables):
    # _, variable, expr = node
    # value = evaluate(expr, variables)
    # return {**variables, variable: value}  # إرجاع نسخة جديدة من القيم

    if node[0] != "Assignment":
        raise ValueError(f"Unexpected node type for assignment: {node[0]}")
    variable = node[1]
    # عشان نعرف نوع المعادله ونحلها
    value = evaluate(node[2], variables)  # 2+5
    variables[variable] = value
    return value

 # if x>5 <<<= if بنحل الجزء اللي قدام

def evaluate_if(node, variables):
    match node:
        case ("If", condition_node, then_node, else_node):
            condition = evaluate(condition_node, variables)  # ده بتحل الكونديشن بناء ع نوعه evaluate وبرجعه لفانكشن  if بشوف اي الشرط بتاع
            return (lambda cond, then_stmt, else_stmt:
                    evaluate(then_stmt, variables) if cond != 0 else  # else لو بفلس هنفذ بتاع ال
                    (evaluate(else_stmt, variables) if else_stmt else None))(
                    condition, then_node, else_node)  # else لو بفولس هنفذ بتاع ال
        case _:
            raise ValueError(f"Unexpected node type for if statement: {node[0]}")


#  statement بشوف نوع ال
def evaluate(node, variables):
    match node:
        case ("Number", _):
            return evaluate_primary(node, variables)
        case ("Variable", _):
            return evaluate_primary(node, variables)
        case ("BinaryOp", _, _, _):
            return evaluate_binop(node, variables)
        case ("Assignment", var_name, expr_node):
            value = evaluate(expr_node, variables)
            variables[var_name] = value
            return variables
        case ("If", _, _, _):
            return evaluate_if(node, variables)
        case _:
            raise ValueError(f"Unexpected node type: {node[0]}")


# ast في ال  statement  باخد كل
def evaluate_statements(statements, variables):
    if not statements:
        return variables
    updated_variables = evaluate(statements[0], variables)

    if isinstance(updated_variables, dict):
        return evaluate_statements(statements[1:], updated_variables)
    else:
        raise ValueError("Expected a dictionary of variables but got a non-dictionary value.")



# input_expr = "x = 2 + 3 * 4; if x >= 3 then y = 2 else y = 6"
# tokens = toknize(input_expr)
# statements = parseer(tokens)
# variables = evaluate_statements(statements, {})

# print(variables)


if __name__ == "__main__":
    input_expr = "x = 2 + 3 * 4; if x >= 3 then y = 2 else y = 6"
    tokens = toknize(input_expr)
    print(tokens)

    statements = parseer(tokens)
    print(statements)
    # main()