def normalize_filters(filters):
    result = []
    expected = 1
    operators = {
        '!': 1,
        '|': 2,
        '&': 2
    }
    for token in filters:
        if expected == 0:
            result.insert(0, '&')
            expected = 1    
        result.append(token)
        if type(token) in (list, tuple):
            expected -= 1
        else:
            nary = operators[token]
            expected += nary - 1
    assert expected == 0, 'Invalid filters syntax'
    return result

def combine_filters(operator, filters_list):
    result = []
    count = 0
    for filters in filters_list:
        result += filters
        count += 1
    result = [operator] * (count - 1) + result
    return result

if __name__ == '__main__':
    a = normalize_filters([('a','=',1)])
    b = normalize_filters([('b','=',1)])
    print(combine_filters('|',[a]))
