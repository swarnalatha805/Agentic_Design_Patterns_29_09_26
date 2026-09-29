import unittest

from tools.calculator import calculator


class CalculatorTests(unittest.TestCase):
    def test_evaluates_arithmetic_expression(self):
        self.assertEqual(calculator("((10 + 5) / 2) ** 2"), "56.25")

    def test_rejects_python_function_calls(self):
        result = calculator("__import__('os').getcwd()")
        self.assertTrue(result.startswith("Error:"))

    def test_rejects_excessively_large_exponents(self):
        result = calculator("2 ** 1001")
        self.assertTrue(result.startswith("Error:"))


if __name__ == "__main__":
    unittest.main()