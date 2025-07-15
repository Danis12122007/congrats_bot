from validators.validators import is_valid_name
import pytest


def test_is_valid_name():
    assert is_valid_name("Маша") == True
    assert is_valid_name("Маша222") == False
    assert is_valid_name("-") == True
    assert is_valid_name("Маша-Анна") == True
    assert is_valid_name("-Маша-Анна") == False
    assert is_valid_name("-Маша-Анна-") == False
    assert is_valid_name("Маша--Анна") == False
    assert is_valid_name("Маша_Анна") == False
    assert is_valid_name("--") == False
    assert is_valid_name("2421") == False
    assert is_valid_name("^*^") == False
