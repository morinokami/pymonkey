from monkey import object


def test_string_hash_key():
    hello1 = object.String('Hello World')
    hello2 = object.String('Hello World')
    diff1 = object.String('My name is johnny')
    diff2 = object.String('My name is johnny')

    assert hello1.hash_key() == hello2.hash_key(), \
        'strings with same content have different hash keys'

    assert diff1.hash_key() == diff2.hash_key(), \
        'strings with same content have different hash keys'

    assert hello1.hash_key() != diff1.hash_key(), \
        'strings with different content have same hash keys'


def test_boolean_hash_key():
    true1 = object.Boolean(True)
    true2 = object.Boolean(True)
    false1 = object.Boolean(False)
    false2 = object.Boolean(False)

    assert true1.hash_key() == true2.hash_key(), \
        'trues do not have same hash key'

    assert false1.hash_key() == false2.hash_key(), \
        'falses do not have same hash key'

    assert true1.hash_key() != false1.hash_key(), \
        'true has same hash key as false'


def test_integer_hash_key():
    one1 = object.Integer(1)
    one2 = object.Integer(1)
    two1 = object.Integer(2)
    two2 = object.Integer(2)

    assert one1.hash_key() == one2.hash_key(), \
        'integers with same content have twoerent hash keys'

    assert two1.hash_key() == two2.hash_key(), \
        'integers with same content have twoerent hash keys'

    assert one1.hash_key() != two1.hash_key(), \
        'integers with tworent content have same hash keys'
