.PHONY: all clean build

all:


build: clean
	mkdir -p build
	python setup.py sdist -d build


clean:
	find . -name __pycache__ -type d | xargs rm -rfv
	rm -rf build

#publish-py:
#	ssh mcn@zero mkdir -p /home/mcn/live/www/py/mcn-core
#	scp build/mcn-core*.tar.gz mcn@zero:~/live/www/py/mcn-core
