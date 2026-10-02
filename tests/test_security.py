from app.security import generate_code, validate_alias

def test_generated_code_has_expected_length():
    code = generate_code()
    assert len(code) == 7
    assert code.isalnum()

def test_alias_validation():
    assert validate_alias("my-campaign_2")
    assert not validate_alias("ab")
    assert not validate_alias("not valid")
    assert not validate_alias("../admin")
