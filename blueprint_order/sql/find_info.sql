select b_id, b_address, b_price, b_size, b_quality, b_date, o_name, o_phone
from billboard join owner using(o_id)
where b_id = '$b_id'