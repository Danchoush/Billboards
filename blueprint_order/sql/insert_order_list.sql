INSERT orderline VALUES(NULL, '$start',(select new_date from (select *, date_add('$start', INTERVAL '$period' MONTH) as new_date
from orderline
 where ol_id = 1) as new_table) , '$b_price','$b_id' ,'$order_id')