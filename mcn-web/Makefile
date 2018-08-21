.PHONY: all clean build


DIR_STATIC = mcn/web/static
SRC_SCSS = mcn/web/assets/scss


all:


build: clean
	mkdir -p build
	python setup.py sdist -d build


clean:
	find . -name __pycache__ -type d | xargs rm -rfv
	rm -rf build


all:


run:
	python mcn/web/app.py


scss:
	mkdir -p $(DIR_STATIC)/css
	python -mscss -C $(SRC_SCSS)/main.scss > $(DIR_STATIC)/css/main.css


publish-py:
	ssh mcn@zero mkdir -p /home/mcn/live/www/py/mcn-web
	scp build/mcn-web*.tar.gz mcn@zero:~/live/www/py/mcn-web
