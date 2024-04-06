from theflow import Function

def square(x: int) -> int:
    return x*x

class MultiplyBy(Function):
    factor: int
    def run(self, y):
        return y*self.factor



class MultiplySquareFlow(Function):
    multiply: Function
    square: Function

    def run(self, x):
        y = self.multiply(x)
        y = self.square(y)
        return y

def multiply_then_square(x: int, multiplication_factor: int) -> int:
    """Multiply x by multiplication factor, then square the result.

    Args:
        x (int): Input number
        multiplication_factor (int): Multiplication factor for x

    Returns:
        int: x times multiplication factor, then the squared result using the provided Functions
    """
    flow = MultiplySquareFlow(square=square,multiply=MultiplyBy(factor=multiplication_factor))
    return flow(x=x)
