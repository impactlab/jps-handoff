#!/bin/bash

mysql impactlab -pimpactlab <<EOF
LOAD DATA LOCAL INFILE '/data/mv90parsed_nightly.csv'
  INTO TABLE viewer_profiledatapoint 
  FIELDS TERMINATED BY ',' 
  OPTIONALLY ENCLOSED BY '"'
  LINES TERMINATED BY '\n'
    (ts, kwh, raw, meter_id);

EOF
