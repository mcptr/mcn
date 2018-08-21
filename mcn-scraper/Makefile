.PHONY: all clean build


all:


build: clean
	mkdir -p build
	python setup.py sdist -d build


clean:
	find . -name __pycache__ -type d | xargs rm -rfv
	find . -name *~ -type f | xargs rm -rfv
	rm -rf build
