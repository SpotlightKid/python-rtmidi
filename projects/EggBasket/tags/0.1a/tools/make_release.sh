#!/bin/bash

# make_release.sh - automates steps to build a EggBasket release

if [ "x$1" = "x-f" ]; then
    FINAL=yes
    shift
fi

SVN_BASE_URL="svn+ssh://svn/coding"
VERSION=$(python -c 'from eggbasket.release import version; print version')
PROJECT_NAME=$(python -c 'from eggbasket.release import name; print name')
HOMEPAGE=$(python -c 'from eggbasket.release import url; print url')

RST2HTML_OPTS='--stylesheet-path=rest.css --link-stylesheet --input-encoding=UTF-8 --output-encoding=UTF-8 --language=en --no-xml-declaration --date --time'

# clean up
find . -name "*.pyc" -o -name "*.pyo" | xargs rm -f
rm -rf build doc/api doc/index.html README.txt*

# create README form template
python tools/make_readme.py README.in README.txt
test $? -eq 0 || exit 1

# convert ReST to HTML
RST2HTML=$(which rst2html 2>/dev/null)
if [ -z "$RST2HTML" ]; then
    RST2HTML=$(which rst2html.py 2>/dev/null)
fi
mkdir -p doc
( cd doc; \
  "$RST2HTML" $RST2HTML_OPTS ../README.txt >index.html; )


# generate API documentation
( cd doc; \
  epydoc --html --url "$HOMEPAGE" --name $PROJECT_NAME \
  --output=api --no-frames -v ../eggbasket; )

# Build distribution packages
if [ "x$FINAL" != "xyes" ]; then
    python setup.py bdist_egg sdist --formats=zip,bztar
    if [ "x$1" = "xupload" ]; then
        ./tools/upload.sh
    fi
else
    # Check if everything is commited
    SVN_STATUS=$(svn status)
    if [ -n "$SVN_STATUS" ]; then
        echo "SVN is not up to date. Please fix." 2>&1
        exit 1
    fi

    # and upload & register them at the Cheeseshop if "-f" option is given
    python setup.py egg_info -RDb "" bdist_egg sdist --formats=zip,bztar \
        register upload
    ret=$?
    # tag release in SVN
    if [ $ret -eq 0 ]; then
        svn copy "$SVN_BASE_URL/$PROJECT_NAME/trunk" \
          "$SVN_BASE_URL/$PROJECT_NAME/tags/$VERSION" \
           -m "Tagging release $VERSION"
    fi
    # update web site
    ./tools/upload.sh
fi
