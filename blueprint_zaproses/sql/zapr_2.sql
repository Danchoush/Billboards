select t_id, t_name, t_phone, t_adress, t_buisness, t_date
from tenant
where t_phone like "$input_phone" ;
