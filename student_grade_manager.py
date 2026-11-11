"""Student Grade Management System

Accepts student marks, calculates average marks and letter grades,
validates every input, and displays the results.

Usage:
    python student_grade_manager.py          run the program
    python student_grade_manager.py --test   run the built-in unit tests

Grading scale:
    A  : 90 - 100
    B  : 80 - 89.99
    C  : 70 - 79.99
    D  : 60 - 69.99
    F  : below 60
"""

import sys
import unittest

MIN_MARK = 0.0
MAX_MARK = 100.0
MAX_NAME_LENGTH = 50

GRADE_SCALE = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
]


# ---------------------------------------------------------------- validation
def validate_name(text):
    """Return a cleaned student name or raise ValueError."""
    name = text.strip()
    if not name:
        raise ValueError("Name cannot be empty.")
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"Name cannot be longer than {MAX_NAME_LENGTH} characters.")
    if not all(ch.isalpha() or ch in " .'-" for ch in name):
        raise ValueError("Name may only contain letters, spaces, '.', ''' and '-'.")
    return name


def validate_mark(text):
    """Return a mark as float, or raise ValueError if it is not valid."""
    text = text.strip()
    if not text:
        raise ValueError("Mark cannot be empty.")
    try:
        mark = float(text)
    except ValueError:
        raise ValueError("Mark must be a number.") from None
    if mark != mark or mark in (float("inf"), float("-inf")):
        raise ValueError("Mark must be a finite number.")
    if not MIN_MARK <= mark <= MAX_MARK:
        raise ValueError(f"Mark must be between {MIN_MARK:g} and {MAX_MARK:g}.")
    return mark


def validate_count(text, label, minimum=1, maximum=50):
    """Return a whole number within [minimum, maximum] or raise ValueError."""
    text = text.strip()
    if not text.isdigit():
        raise ValueError(f"{label} must be a whole number.")
    value = int(text)
    if not minimum <= value <= maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}.")
    return value


# --------------------------------------------------------------- calculation
def calculate_average(marks):
    """Return the average of a non-empty list of marks."""
    if not marks:
        raise ValueError("At least one mark is required.")
    return sum(marks) / len(marks)


def letter_grade(average):
    """Convert an average mark to a letter grade."""
    if not MIN_MARK <= average <= MAX_MARK:
        raise ValueError("Average must be between 0 and 100.")
    for threshold, letter in GRADE_SCALE:
        if average >= threshold:
            return letter
    return "F"


def build_record(name, marks):
    """Create a result record for one student."""
    average = calculate_average(marks)
    return {
        "name": name,
        "marks": list(marks),
        "average": average,
        "grade": letter_grade(average),
    }


def class_summary(records):
    """Return class average, highest and lowest student averages."""
    if not records:
        raise ValueError("No student records.")
    averages = [r["average"] for r in records]
    best = max(records, key=lambda r: r["average"])
    worst = min(records, key=lambda r: r["average"])
    return {
        "class_average": sum(averages) / len(averages),
        "highest": best,
        "lowest": worst,
    }


# ------------------------------------------------------------------- display
def format_results(records):
    """Return the results table and class summary as a string."""
    width = 62
    lines = ["", "=" * width, "STUDENT RESULTS".center(width), "=" * width]
    lines.append(f"{'No.':<5}{'Name':<28}{'Subjects':>9}{'Average':>10}{'Grade':>8}")
    lines.append("-" * width)
    for i, r in enumerate(records, start=1):
        lines.append(
            f"{i:<5}{r['name']:<28}{len(r['marks']):>9}{r['average']:>10.2f}{r['grade']:>8}"
        )
    lines.append("-" * width)
    summary = class_summary(records)
    lines.append(f"Class average : {summary['class_average']:.2f}")
    lines.append(
        f"Highest       : {summary['highest']['name']} "
        f"({summary['highest']['average']:.2f}, {summary['highest']['grade']})"
    )
    lines.append(
        f"Lowest        : {summary['lowest']['name']} "
        f"({summary['lowest']['average']:.2f}, {summary['lowest']['grade']})"
    )
    lines.append("=" * width)
    return "\n".join(lines)


# --------------------------------------------------------------------- input
def prompt(message, validator, *args):
    """Keep asking until the validator accepts the input."""
    while True:
        try:
            return validator(input(message), *args)
        except ValueError as error:
            print(f"  Invalid input: {error}")


def read_student(number):
    name = prompt(f"Student {number} name: ", validate_name)
    subjects = prompt(f"  Number of subjects for {name}: ", validate_count, "Number of subjects")
    marks = []
    for s in range(1, subjects + 1):
        marks.append(prompt(f"  Mark for subject {s} (0-100): ", validate_mark))
    return build_record(name, marks)


def main():
    print("STUDENT GRADE MANAGEMENT SYSTEM")
    print("-" * 31)
    count = prompt("How many students? ", validate_count, "Number of students", 1, 200)
    records = [read_student(n) for n in range(1, count + 1)]
    print(format_results(records))


# ==========================================================================
# UNIT TESTS
# ==========================================================================

class TestValidation(unittest.TestCase):
    def test_valid_marks(self):
        self.assertEqual(validate_mark("0"), 0.0)
        self.assertEqual(validate_mark("100"), 100.0)
        self.assertEqual(validate_mark(" 75.5 "), 75.5)

    def test_invalid_marks(self):
        for bad in ["", "abc", "-1", "100.1", "101", "nan", "inf", "5,5"]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    validate_mark(bad)

    def test_valid_names(self):
        self.assertEqual(validate_name("  Selam Tadesse "), "Selam Tadesse")
        self.assertEqual(validate_name("Mary-Ann O'Neil"), "Mary-Ann O'Neil")

    def test_invalid_names(self):
        for bad in ["", "   ", "Abel123", "Abel@", "x" * 51]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    validate_name(bad)

    def test_count(self):
        self.assertEqual(validate_count("3", "n"), 3)
        for bad in ["0", "-2", "2.5", "", "abc", "51"]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    validate_count(bad, "n")


class TestCalculation(unittest.TestCase):
    def test_average(self):
        self.assertAlmostEqual(calculate_average([80, 90, 100]), 90.0)
        self.assertAlmostEqual(calculate_average([70]), 70.0)

    def test_average_empty(self):
        with self.assertRaises(ValueError):
            calculate_average([])

    def test_letter_grade_boundaries(self):
        cases = {
            100: "A", 90: "A", 89.99: "B", 80: "B", 79.99: "C",
            70: "C", 69.99: "D", 60: "D", 59.99: "F", 0: "F",
        }
        for average, expected in cases.items():
            with self.subTest(average=average):
                self.assertEqual(letter_grade(average), expected)

    def test_letter_grade_out_of_range(self):
        for bad in (-0.1, 100.1):
            with self.assertRaises(ValueError):
                letter_grade(bad)

    def test_build_record(self):
        record = build_record("Abel", [85, 95])
        self.assertEqual(record["average"], 90.0)
        self.assertEqual(record["grade"], "A")

    def test_class_summary(self):
        records = [build_record("A", [90]), build_record("B", [50])]
        summary = class_summary(records)
        self.assertEqual(summary["class_average"], 70.0)
        self.assertEqual(summary["highest"]["name"], "A")
        self.assertEqual(summary["lowest"]["name"], "B")


class TestDisplay(unittest.TestCase):
    def test_format_results_contains_data(self):
        records = [build_record("Abel", [85, 95]), build_record("Selam", [55, 65])]
        text = format_results(records)
        self.assertIn("Abel", text)
        self.assertIn("90.00", text)
        self.assertIn("Class average", text)


def run_tests():
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.exit(run_tests())
    main()
