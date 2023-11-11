def get_es_bulk_query(es_data: list, es_index: str, es_id_field: str) -> list[dict]:
    for row in es_data:
        yield {
            '_index': es_index,
            '_id': row[es_id_field],
            '_source': row,
        }
