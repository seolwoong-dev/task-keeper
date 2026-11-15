from sqlalchemy import event


def test_list_tasks_query_count(client, db_session):
    # 태그가 붙은 할 일이 여러 개여도 GET /tasks 는 2회(할 일 + 태그 IN)만 조회해야 합니다.
    for i in range(3):
        client.post("/tasks", json={"title": f"할 일 {i}", "tags": [f"태그{i}", "공통"]})

    statements: list[str] = []
    engine = db_session.get_bind()

    def count(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", count)
    try:
        res = client.get("/tasks")
    finally:
        event.remove(engine, "before_cursor_execute", count)

    assert res.status_code == 200
    assert all(t["tags"] for t in res.json())
    assert len(statements) == 2, "\n\n".join(statements)
