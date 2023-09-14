insert into schedule values(NULL, '$s_start', (select new_date from (select *, date_add('$s_start', INTERVAL '$period' MONTH) as new_date
from schedule
 where s_id =1) as new_table) , '$b_id')