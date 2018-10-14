#!/bin/bash

cd /backup/.snapshots/daily.0/akkserv/mnt/akkserv-raid
DBPATH=/root/
GITPATH=${DBPATH}/StructureFinder/
rm ${DBPATH}/structurefinder_new.sqlite

LOGFILE=/var/log/strf.log
touch ${LOGFILE}
echo " " >> ${LOGFILE}
echo "####################################################################################" >> ${LOGFILE}
echo "Start DB creation at: "$(date) "------------------------------------" >> ${LOGFILE}

# Be aware that we are in the directory selected above!
# option -r activates indexing of .res files, -c .cif files.
python3 ${GITPATH}/strf_cmd.py -c -r \
-d home/akbutschke \
-d home/akboettcher \
-d home/wissang/ \
-d xray \
-d public/wissang/Ehemalige \
-o ${DBPATH}/structurefinder_new.sqlite >> ${LOGFILE}

echo "DB creation finished at: "$(date) "------------------------------------" >> ${LOGFILE}

rm ${DBPATH}/structurefinder.sqlite
mv ${DBPATH}/structurefinder_new.sqlite ${DBPATH}/structurefinder.sqlite
# To restart the web server:
touch ${GITPATH}/strf_cmd.py