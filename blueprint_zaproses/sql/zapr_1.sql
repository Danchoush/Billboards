SELECT t_id, t_name, t_phone, t_adress, t_buisness, t_date
FROM tenant
WHERE MONTH(t_date) = "$input_month" and YEAR(t_date)="$input_year";

