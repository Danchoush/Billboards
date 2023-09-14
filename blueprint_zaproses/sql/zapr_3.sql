select sum(or_price), t_id
from orders join tenant using(t_id)
where t_name ="$input_name"
group by t_id;

