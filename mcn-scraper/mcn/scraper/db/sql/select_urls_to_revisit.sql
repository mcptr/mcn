SELECT
	U.*,
	(EXTRACT(EPOCH FROM NOW()) - EXTRACT('EPOCH' FROM mtime))::INTEGER AS age
	FROM urls U
	WHERE EXTRACT(EPOCH FROM U.mtime)::INTEGER >= %(age)s
	ORDER BY U.id ASC, U.mtime DESC
	LIMIT %(limit)s OFFSET %(offset)s

