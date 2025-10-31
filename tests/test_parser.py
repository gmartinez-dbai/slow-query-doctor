from slowquerydoctor import parser

def test_multiline_query_parsing(tmp_path):
    log_content = '''
2025-10-28 10:15:30.123 UTC [12345]: [1-1] user=postgres,db=myapp LOG:  duration: 156.789 ms  statement: SELECT *\nFROM users\nWHERE email LIKE '%@example.com';
2025-10-28 10:16:30.123 UTC [12345]: [1-1] user=postgres,db=myapp LOG:  duration: 200.000 ms  statement: UPDATE users SET name = 'O\'Reilly' WHERE id = 1;
'''
    log_file = tmp_path / "test.log"
    log_file.write_text(log_content)
    df = parser.parse_postgres_log(str(log_file))
    assert len(df) == 2
    assert "SELECT *" in df.iloc[0]["query"]
    assert "FROM users" in df.iloc[0]["query"]
    assert "O'Reilly" in df.iloc[1]["query"]

def test_unusual_characters(tmp_path):
    log_content = '''
2025-10-28 10:17:30.123 UTC [12345]: [1-1] user=postgres,db=myapp LOG:  duration: 300.000 ms  statement: SELECT * FROM users WHERE name = '测试用户';
'''
    log_file = tmp_path / "test_unicode.log"
    log_file.write_text(log_content)
    df = parser.parse_postgres_log(str(log_file))
    assert len(df) == 1
    assert "测试用户" in df.iloc[0]["query"]
