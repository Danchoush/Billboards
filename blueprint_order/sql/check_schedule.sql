select s_start, s_end
from schedule
where b_id = '$b_id' and s_start >= '$today'