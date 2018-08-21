def mk_pagination(endpoint, dataset, page_id, limit, **params):
    prev_enabled = page_id > 1
    next_enabled = len(dataset) >= limit

    return dict(
        endpoint=endpoint,
        current_page=page_id,
        next_enabled=next_enabled,
        prev_enabled=prev_enabled,
        prev_page_id=(page_id - 1 if prev_enabled else 1),
        next_page_id=(page_id + 1 if next_enabled else page_id),
        params=params
    )

