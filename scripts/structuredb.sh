#!/bin/bash

cd /backup/.snapshots/daily.0/akkserv/mnt/akkserv-raid
DBPATH=/srv/www/cgi-bin/
DATE=$(date)
rm $DBPATH/structurefinder.sqlite

LOGFILE=/var/log/strf.log
touch $LOGFILE
echo " " >> $LOGFILE
echo "Start DB creation at: "$DATE >> $LOGFILE

# Be aware that we are in the directory selected above!
python3 /root/StructureFinder/strf_cmd.py \
-d home/akbutschke \
-d home/akboettcher \
-d home/wissang/ \
-d xray \
-d public/wissang/Ehemalige \
-o $DBPATH/structurefinder.sqlite >> $LOGFILE

echo "DB creation finished at: "$DATE >> $LOGFILE
