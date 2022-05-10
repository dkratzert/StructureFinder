#!/bin/bash

DBPATH='.'
GITPATH=${DBPATH}/StructureFinder/
rm ${DBPATH}/structurefinder_new.sqlite

LOGFILE=/var/log/strf.log
touch ${LOGFILE}
echo " " >> ${LOGFILE}
echo "####################################################################################" >> ${LOGFILE}
echo "Start DB creation at: '$(date) '------------------------------------" >> ${LOGFILE}

# Be aware that we are in the directory selected above!
# option -r activates indexing of .res files, -c .cif files.
python3 -u ${GITPATH}/strf_cmd.py -c -r \
-d home/akbutschke \
-d home/akboettcher \
-d home/wissang/ \
-d xray \
-d public/wissang/Ehemalige \
-o ${DBPATH}/structurefinder_new.sqlite >> ${LOGFILE}

echo "DB creation finished at: '$(date) '------------------------------------" >> ${LOGFILE}

rm ${DBPATH}/structurefinder.sqlite
mv ${DBPATH}/structurefinder_new.sqlite ${DBPATH}/structurefinder.sqlite
# To restart the web server:
touch ${GITPATH}/cgi_ui/cgi-bin/strf_web.py