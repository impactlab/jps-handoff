ALTER SESSION SET CURRENT_SCHEMA = UIMSMGR

set term off
set echo off
set underline off
set colsep “;”
set linesize 100
set pagesize 0
set sqlprompt ”
set lines 1000 pages 1000
set trimspool on
set feedback off
set heading on
set newpage 0
set headsep off

spool meter_map.csv
select distinct UBBCHST_INVN_CODE, UBBCHST_CUST_CODE, UBBCHST_PREM_CODE from UBBCHST WHERE UBBCHST_INVN_CODE IS NOT NULL;
spool off;
exit;
/