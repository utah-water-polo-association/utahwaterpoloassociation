#! /bin/bash
cp -fR public/* output/
(cd content && find . -name '*.jpeg' -exec rsync -R {} ../output/ \;)
(cd content && find . -name '*.png' -exec rsync -R {} ../output/ \;)
(cd content && find . -name '*.jpg' -exec rsync -R {} ../output/ \;)
(cd content && find . -name '*.pdf' -exec rsync -R {} ../output/ \;)