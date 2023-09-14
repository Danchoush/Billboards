SELECT MAX(or_id) AS max_id
    FROM orders
    WHERE t_id = '$user_id'