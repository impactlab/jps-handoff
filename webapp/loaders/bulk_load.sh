#!/bin/bash

datadir=/data/nightly_extract
meters=$(cat meter_list.csv | sed 's/,/\n/g')

for meter in $meters ; do 
  profile_file=$(ls $datadir/${meter}__* | head -1)
  evt_file=$(ls $datadir/evt__${meter}__* | head -1)
  if [[ $profile_file == "" ]] ; then continue ; fi
  dos2unix $profile_file
  echo $meter
  mysql -u impactlab -pimpactlab impactlab <<EOF
  INSERT INTO viewer_meter 
    (meter_id, user_id, overall_score, on_auditlist)
    SELECT '$meter', 2, 0.0, false
    WHERE NOT EXISTS 
    (SELECT id FROM viewer_meter WHERE meter_id='$meter');
EOF
  if [[ $(wc $profile_file | awk '{print $1}') -gt 0 ]] ; then
    echo "  profile"
    mysql -u impactlab -pimpactlab impactlab <<EOF
  DROP TABLE IF EXISTS dummy;
  CREATE TABLE dummy 
    (meter_id VARCHAR, ts TIMESTAMP, kwh FLOAT, kva FLOAT);
  \COPY dummy FROM $profile_file CSV
  INSERT INTO viewer_profiledatapoint (meter_id, ts, kwh, kva) 
    SELECT m.id, d.ts, d.kwh, d.kva 
     FROM viewer_meter m JOIN dummy d ON m.meter_id=d.meter_id;
EOF
  fi
  if [[ $evt_file != "" ]] ; then
    dos2unix $evt_file
    if [ "$(tail -1 $evt_file | awk '{print $1}')" == "Total:" ] ; then 
      cat $evt_file | head -n -1 > ${evt_file}.tmp
      mv ${evt_file}.tmp $evt_file
    fi
    if [[ $(wc $evt_file | awk '{print $1}') -gt 1 ]] ; then
      echo "  event"
      mysql -u impactlab -pimpactlab impactlab <<EOF
  DROP TABLE IF EXISTS dummy;
  CREATE TABLE dummy 
    (meter_id VARCHAR, ts TIMESTAMP, event VARCHAR);
  \COPY dummy FROM $evt_file CSV HEADER
  INSERT INTO viewer_eventdatapoint (meter_id, ts, event) 
    SELECT m.id, d.ts, d.event 
     FROM viewer_meter m JOIN dummy d ON m.meter_id=d.meter_id;
EOF
    fi
  fi

done
