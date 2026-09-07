"""Unit tests for template variable rendering."""
import unittest

from agentic_setup.errors import UsageError
from agentic_setup.render import render, variable_names


class RenderTests(unittest.TestCase):
    def test_substitutes_known_variable(self):
        self.assertEqual(render("Hello {{NAME}}!", {"NAME": "world"}), "Hello world!")

    def test_substitutes_every_occurrence(self):
        self.assertEqual(render("{{N}} and {{N}}", {"N": "x"}), "x and x")

    def test_rejects_unknown_variable_naming_it(self):
        with self.assertRaises(UsageError) as ctx:
            render("Hi {{WHO}}", {"NAME": "x"})
        self.assertIn("WHO", str(ctx.exception))

    def test_leaves_github_expression_syntax_alone(self):
        text = "run: echo ${{ matrix.foo }}"
        self.assertEqual(render(text, {}), text)

    def test_value_braces_are_not_recursively_expanded(self):
        self.assertEqual(render("{{V}}", {"V": "{{V}}"}), "{{V}}")

    def test_rejects_non_string_value(self):
        with self.assertRaises(UsageError):
            render("{{V}}", {"V": 3})

    def test_variable_names_are_sorted_and_unique(self):
        self.assertEqual(variable_names("{{B}} {{A}} {{A}}"), ["A", "B"])


if __name__ == "__main__":
    unittest.main()
