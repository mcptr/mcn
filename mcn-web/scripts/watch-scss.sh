#!/bin/sh

while inotifywait -r mcn/web/assets/scss/*; do
    make scss
done
