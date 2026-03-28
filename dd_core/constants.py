"""Constants shared across the Double-digits lab."""

from __future__ import annotations

SINGLE_LEVEL = "single"
DOUBLE_LEVEL = "double"
ARITHMETIC_LEVEL = "arithmetic"

LEVELS = (SINGLE_LEVEL, DOUBLE_LEVEL, ARITHMETIC_LEVEL)

DIGIT_SIZE = (28, 28)
DOUBLE_SCENE_SIZE = (28, 56)
ARITHMETIC_SCENE_SIZE = (28, 84)

OPERATORS = {
    "add": {
        "symbol": "+",
        "label": "Addition",
        "description": "Combine two single digits by summing them.",
    },
    "subtract": {
        "symbol": "-",
        "label": "Subtraction",
        "description": "Subtract the smaller digit from the larger one so the result stays non-negative.",
    },
    "multiply": {
        "symbol": "×",
        "label": "Multiplication",
        "description": "Multiply the two recognized digits.",
    },
}

CURATED_EXAMPLES = {
    SINGLE_LEVEL: [
        {"id": "single_0", "digit": 0, "variant": 2, "title": "Round zero"},
        {"id": "single_1", "digit": 1, "variant": 5, "title": "Tall one"},
        {"id": "single_3", "digit": 3, "variant": 8, "title": "Open three"},
        {"id": "single_5", "digit": 5, "variant": 4, "title": "Busy five"},
        {"id": "single_7", "digit": 7, "variant": 7, "title": "Angular seven"},
        {"id": "single_9", "digit": 9, "variant": 3, "title": "Looped nine"},
    ],
    DOUBLE_LEVEL: [
        {"id": "double_12", "left": 1, "right": 2, "left_variant": 4, "right_variant": 7, "title": "Twelve"},
        {"id": "double_27", "left": 2, "right": 7, "left_variant": 11, "right_variant": 9, "title": "Twenty-seven"},
        {"id": "double_40", "left": 4, "right": 0, "left_variant": 6, "right_variant": 2, "title": "Forty"},
        {"id": "double_56", "left": 5, "right": 6, "left_variant": 8, "right_variant": 5, "title": "Fifty-six"},
        {"id": "double_83", "left": 8, "right": 3, "left_variant": 4, "right_variant": 10, "title": "Eighty-three"},
        {"id": "double_90", "left": 9, "right": 0, "left_variant": 3, "right_variant": 1, "title": "Ninety"},
    ],
    ARITHMETIC_LEVEL: [
        {"id": "arith_add_37", "left": 3, "right": 7, "operator": "add", "left_variant": 8, "right_variant": 3, "title": "3 + 7"},
        {"id": "arith_sub_82", "left": 8, "right": 2, "operator": "subtract", "left_variant": 4, "right_variant": 6, "title": "8 - 2"},
        {"id": "arith_mul_34", "left": 3, "right": 4, "operator": "multiply", "left_variant": 2, "right_variant": 7, "title": "3 × 4"},
        {"id": "arith_add_58", "left": 5, "right": 8, "operator": "add", "left_variant": 10, "right_variant": 5, "title": "5 + 8"},
        {"id": "arith_sub_91", "left": 9, "right": 1, "operator": "subtract", "left_variant": 1, "right_variant": 11, "title": "9 - 1"},
        {"id": "arith_mul_67", "left": 6, "right": 7, "operator": "multiply", "left_variant": 9, "right_variant": 8, "title": "6 × 7"},
    ],
}
