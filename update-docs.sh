#!/bin/bash
#
# update-docs.sh - Build documentation, update gh-pages branch and push changes

git checkout master || exit 1
git pull
make docs
git checkout gh-pages || exit 1
rsync -av docs/_build/html/ .
git add -A
COMMIT="$(git log -n 1 --pretty=format:"%h" master)"
git commit -m "Update docs for commit $COMMIT"
git push
git checkout master
