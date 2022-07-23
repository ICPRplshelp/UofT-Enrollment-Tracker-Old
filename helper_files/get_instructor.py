"""I need the instructor. Right now."""
import json
import time
from typing import Any


class LecInfoGetter:
    data: dict[str, Any]

    def __init__(self) -> None:
        with open('outputInstructors.json', encoding='UTF-8') as f:
            self.data = json.load(f)

    def get_instructor(self, full_course_code: str) -> str:
        return self.data.get(full_course_code, 'N/A')


if __name__ == '__main__':
    t1 = time.perf_counter()
    cig = LecInfoGetter()
    temp_ins = cig.get_instructor('CSC110Y1-F-20229-LEC-0101')
    t2 = time.perf_counter()
    print(temp_ins)
    print(t2 - t1)
