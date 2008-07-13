#!/bin/sh

# make_release.sh - automates steps to build a FancyFlashExample release

if [ "x$1" = "x-f" ]; then
    FINAL=yes
    shift
fi

SVN_BASE_URL="svn+ssh://svn/coding"
VERSION=$(python -c 'from fflashex.release import version; print version')
PROJECT_NAME=$(python -c 'from fflashex.release import name; print name')
HOMEPAGE=$(python -c 'from fflashex.release import url; print url')

RST2HTML_OPTS='--stylesheet-path=rest.css --link-stylesheet --input-encoding=UTF-8 --output-encoding=UTF-8 --language=en --no-xml-declaration'

# clean up
find . -name "*.pyc" -o -name "*.pyo" | xargs rm -f
rm -rf build dist README.html

# create README from template
#~ python make_readme.py README.in README.txt
#~ test $? -eq 0 || exit 1

# convert ReST to HTML
RST2HTML=$(which rst2html 2>/dev/null)
if [ -z "$RST2HTML" ]; then
    RST2HTML=$(which rst2html.py 2>/dev/null)
fi
"$RST2HTML" $RST2HTML_OPTS --date --time README.txt >README.html


# Build distribution packages
if [ "x$FINAL" != "xyes" ]; then
    python setup.py sdist --formats=zip,bztar
    python setup.py bdist_egg
    if [ "x$1" = "xupload" ]; then
        ./upload.sh
    fi
else
    # Check if everything is commited
    SVN_STATUS=$(svn status)
    if [ -n "$SVN_STATUS" ]; then
        echo "SVN is not up to date. Please fix." 2>&1
        exit 1
    fi

    # tag release in SVN
    echo svn copy "$SVN_BASE_URL/$PROJECT_NAME/trunk" \
      "$SVN_BASE_URL/$PROJECT_NAME/tags/$VERSION" -m "Tagging release $VERSION"
    #~ # and upload & register them at the Cheeseshop if "-f" option is given 
    #~ python setup.py register
    #~ python setup.py sdist --formats=zip,bztar upload
    #~ python setup.py bdist_egg upload
    # update web site
    ./upload.sh
fi
