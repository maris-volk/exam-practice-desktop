import random
from typing import List

class CaptchaService:
    def __init__(self, correct_order: List[int]):
        self.correct_order = correct_order

    def shuffle(self) -> List[int]:
        order = self.correct_order.copy()
        while order == self.correct_order:
            random.shuffle(order)
        return order

    def is_solved(self, current_order: List[int]) -> bool:
        return current_order == self.correct_order

    def swap(self, order: List[int], i: int, j: int) -> List[int]:
        new_order = order.copy()
        new_order[i], new_order[j] = new_order[j], new_order[i]
        return new_order