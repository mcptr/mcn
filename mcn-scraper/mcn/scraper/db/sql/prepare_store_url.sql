PREPARE st_insert_url AS
	INSERT INTO urls AS U(
	   url, domain_id, headers, content_type, content_size
      	)
      	VALUES($1, $2, $3, $4, $5)
	ON CONFLICT(url) DO UPDATE SET 
	   mtime = NOW(), hits = U.hits + 1,
	   headers=$3
	RETURNING *
