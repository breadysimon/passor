set -x
WRK_DIR=/html_gen
SRC_DIR=$WRK_DIR/bdd-testcases
HTML_DIR=/html

if [ -e $SRC_DIR ] ; then
    cd $SRC_DIR
    git pull
else
    cd $WRK_DIR
    git clone x.git
fi

OUT_DIR=`mktemp -d /tmp/html.XXXXXXXXXX`

cd $WRK_DIR
node html_gen.js $SRC_DIR/testcases $OUT_DIR/html

#awk '{gsub(/\"Given /,"\"设 ");gsub(/\"When /,"\"当 "); gsub(/\"Then /,"\"则 ");  print $0}' data.js >/tmp/data.js

rm -rf $HTML_DIR
mv $OUT_DIR/html $HTML_DIR

rm -rf /tmp/html.*
