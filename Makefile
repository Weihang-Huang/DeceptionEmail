SHELL := /bin/bash
PYTHON ?= python
CONFIG ?= configs/default.yaml

.PHONY: setup test audit experiment report paper verify all

setup:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements-lock.txt

test:
	. .venv/bin/activate && PYTHONHASHSEED=42 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 $(PYTHON) -m pytest -q

audit:
	. .venv/bin/activate && deceptive-email audit --config $(CONFIG)

experiment:
	. .venv/bin/activate && deceptive-email run --config $(CONFIG)

report:
	. .venv/bin/activate && deceptive-email report --config $(CONFIG)

paper:
	. .venv/bin/activate && deceptive-email build-paper --config $(CONFIG)

verify:
	. .venv/bin/activate && deceptive-email verify-manuscript --config $(CONFIG)

all: test audit experiment report paper verify
	@echo "deceptive-email: all stages complete"
