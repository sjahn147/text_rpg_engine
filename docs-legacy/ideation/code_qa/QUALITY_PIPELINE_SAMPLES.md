# 품질 파이프라인 샘플 (pre-commit / CI)

## pre-commit (예시)
```
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.6.1
    hooks:
      - id: mypy
        args: ["--no-warn-no-return", "--strict"]
```

## GitHub Actions CI (예시)
```
name: quality
on: [push, pull_request]
jobs:
  test-type-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest coverage mypy flake8
      - name: Type check (MUST)
        run: mypy .
      - name: Lint (SHOULD)
        run: flake8 .
      - name: Tests + Coverage (SHOULD 80%)
        run: |
          coverage run -m pytest -q
          coverage report --fail-under=80
```

참고: 품질 기준 및 차단 조건은 `docs/rules/04_QUALITY_RULES.yml`을 따릅니다.
