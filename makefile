clean:
	find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
