# Step 1: Tokenization
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def peek(self):
        """Peek at the next character without advancing."""
        next_pos = self.pos + 1
        return self.text[next_pos] if next_pos < len(self.text) else None

    def tokenize(self):
        tokens = []
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                tokens.append(self.number())
            elif self.current_char.isalpha():
                token = self.identifier()
                if token.value in {"if", "else", "while"}:  # Recognize keywords
                    token.type = "KEYWORD"
                tokens.append(token)
            elif self.current_char in '+-*/=><':
                if self.current_char == '=' and self.peek() == '=':
                    tokens.append(Token("OPERATOR", "=="))
                    self.advance()
                elif self.current_char == '!' and self.peek() == '=':
                    tokens.append(Token("OPERATOR", "!="))
                    self.advance()
                elif self.current_char == '<' and self.peek() == '=':
                    tokens.append(Token("OPERATOR", "<="))
                    self.advance()
                elif self.current_char == '>' and self.peek() == '=':
                    tokens.append(Token("OPERATOR", ">="))
                    self.advance()
                else:
                    tokens.append(Token("OPERATOR", self.current_char))
                self.advance()
            elif self.current_char == ';':
                tokens.append(Token("SEMICOLON", self.current_char))
                self.advance()
            elif self.current_char == '(' or self.current_char == ')':
                tokens.append(Token("PAREN", self.current_char))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token("LBRACE", self.current_char))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token("RBRACE", self.current_char))
                self.advance()
            else:
                raise ValueError(f"Invalid character: {self.current_char}")
        return tokens

    def number(self):
        num = ""
        while self.current_char and self.current_char.isdigit():
            num += self.current_char
            self.advance()
        return Token("NUMBER", int(num))

    def identifier(self):
        id_str = ""
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()
        return Token("IDENTIFIER", id_str)

# Step 2: Parsing (AST construction)
class ASTNode:
    pass

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

class BinaryOperation(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Assignment(ASTNode):
    def __init__(self, variable, expression):
        self.variable = variable
        self.expression = expression

class IfStatement(ASTNode):
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block

class WhileLoop(ASTNode):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def consume(self, expected_type):
        token = self.tokens[self.pos]
        if token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type}")
        self.pos += 1
        return token

    def parse(self):
        statements = []
        while self.pos < len(self.tokens):
            statements.append(self.statement())
        return statements

    def statement(self):
        token = self.tokens[self.pos]
        if token.type == "KEYWORD":
            if token.value == "if":
                return self.if_statement()
            elif token.value == "while":
                return self.while_loop()
        elif token.type == "IDENTIFIER":
            return self.assignment()
        else:
            raise ValueError(f"Invalid statement at {token}")

    def assignment(self):
        variable = self.consume("IDENTIFIER").value
        self.consume("OPERATOR")  # '='
        expression = self.expression()
        self.consume("SEMICOLON")
        return Assignment(variable, expression)

    def if_statement(self):
        self.consume("KEYWORD")  # 'if'
        self.consume("PAREN")  # '('
        condition = self.expression()
        self.consume("PAREN")  # ')'
        true_block = self.block()
        false_block = None
        if self.pos < len(self.tokens) and self.tokens[self.pos].value == "else":
            self.consume("KEYWORD")  # 'else'
            false_block = self.block()
        return IfStatement(condition, true_block, false_block)

    def while_loop(self):
        self.consume("KEYWORD")  # 'while'
        self.consume("PAREN")  # '('
        condition = self.expression()
        self.consume("PAREN")  # ')'
        block = self.block()
        return WhileLoop(condition, block)

    def block(self):
        self.consume("LBRACE")
        statements = []
        while self.pos < len(self.tokens) and self.tokens[self.pos].type != "RBRACE":
            statements.append(self.statement())
        self.consume("RBRACE")
        return statements

    def expression(self):
        left = self.term()
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == "OPERATOR":
            operator = self.consume("OPERATOR").value
            right = self.term()
            left = BinaryOperation(left, operator, right)
        return left

    def term(self):
        token = self.tokens[self.pos]
        if token.type == "NUMBER":
            self.consume("NUMBER")
            return Number(token.value)
        elif token.type == "IDENTIFIER":
            self.consume("IDENTIFIER")
            return token.value  # Variable reference
        else:
            raise ValueError(f"Unexpected token {token}")

# Step 3: Evaluation
class Evaluator:
    def __init__(self):
        self.variables = {}

    def evaluate(self, node):
        if isinstance(node, Number):
            return node.value
        elif isinstance(node, str):  # Variable reference
            if node in self.variables:
                return self.variables[node]
            else:
                raise ValueError(f"Undefined variable: {node}")
        elif isinstance(node, BinaryOperation):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.operator == '+':
                return left + right
            elif node.operator == '-':
                return left - right
            elif node.operator == '*':
                return left * right
            elif node.operator == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                return left / right
            elif node.operator == '==':
                return left == right
            elif node.operator == '!=':
                return left != right
            elif node.operator == '<':
                return left < right
            elif node.operator == '>':
                return left > right
            elif node.operator == '<=':
                return left <= right
            elif node.operator == '>=':
                return left >= right
        elif isinstance(node, Assignment):
            value = self.evaluate(node.expression)
            self.variables[node.variable] = value
            return value
        elif isinstance(node, IfStatement):
            condition = self.evaluate(node.condition)
            if condition:
                for stmt in node.true_block:
                    self.evaluate(stmt)
            elif node.false_block:
                for stmt in node.false_block:
                    self.evaluate(stmt)
        elif isinstance(node, WhileLoop):
            while self.evaluate(node.condition):
                for stmt in node.block:
                    self.evaluate(stmt)
        else:
            raise ValueError(f"Invalid node: {node}")

# Step 4: Example Usage
def main():
    text = """
    x = 10;
    if (x > 5) {
        y = x * 2;
    } else {
        y = x + 2;
    }
    z = 0;
    while (z < 5) {
        z = z + 1;
    }
    """
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    print("token:", tokens)

    parser = Parser(tokens)
    evaluator = Evaluator()

    statements = parser.parse()
    print("parser",statements)
    for stmt in statements:
        evaluator.evaluate(stmt)

    print("Variables:", evaluator.variables)

# if __name__ == "__main__":
#     main()
