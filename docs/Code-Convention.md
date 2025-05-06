# 코드 컨벤션

## 사용 언어
- Python

## 기본 규칙
- 들여쓰기(Indentation): 4칸 (스페이스 사용)
- 최대 줄 길이: 79자
- 함수/변수명: snake_case
- 클래스명: PascalCase
- 상수: UPPER_SNAKE_CASE
- 불필요한 공백 금지:
    -  a = 1 (O) / a=1 (X)

## 정렬, 줄바꿈
- 불필요한 줄바꿈 피하기
- 함수 간에는 2줄 띄우기
- import는 표준 -> 서드파티 -> 로컬 순서로 정리하고 각각은 빈 줄로 구분

## 컨벤션 예시
```python
import os
import sys

import requests

from my_module import something

class TestClass():
    print("Something")


def test_function():
    print("Something")

```

