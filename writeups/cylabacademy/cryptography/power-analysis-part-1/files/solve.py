from pwn import *
import numpy, scared, random, string
from estraces import read_ths_from_ram

context.log_level = "error"

# random 16-byte plaintexts, i.e. 32 hex chars
hex_alphabet = string.hexdigits[:16]  # drop the uppercase ABCDEF


def connect_input_and_output(payload, portnumber):
    connection = remote("saturn.picoctf.net", portnumber)
    connection.recvuntil(b"hex: ")

    connection.sendline(payload.encode())
    readoutput = connection.recvline().strip().decode()

    # "... result:  [105, 68, 32, ...]"
    result_currently = readoutput.split("result:  ")[1]
    result_without_braces = result_currently.strip("[").strip("]")
    result_into_a_list_of_int = [int(i) for i in result_without_braces.split(", ")]

    connection.close()

    return result_into_a_list_of_int


def generate_plaintexts(amount) -> list:
    plaintext_list = []
    for i in range(amount):
        rand_32_hex = "".join(random.choices(hex_alphabet, k=32))
        plaintext_list.append(rand_32_hex)
    return plaintext_list


def turn_hexlist_into_list_of_ints(list_of_hexes):
    list_of_list_of_ints = []
    for hexer in list_of_hexes:
        byted_hexes = bytes.fromhex(hexer)
        list_of_ints = [int(byte) for byte in byted_hexes]
        list_of_list_of_ints.append(list_of_ints)
    return list_of_list_of_ints


def send_payloads_and_make_lists(plaintext_amount, portnumber):
    rand_hex_list = generate_plaintexts(plaintext_amount)

    output_list_of_lists = []
    for hexcode in rand_hex_list:
        output_list_of_lists.append(connect_input_and_output(hexcode, portnumber))

    plaintext_input = turn_hexlist_into_list_of_ints(rand_hex_list)

    return plaintext_input, output_list_of_lists


plaintexts, heat_data = send_payloads_and_make_lists(300, 49404)

heat_array = numpy.array(heat_data, dtype="float32")
plaintext_array = numpy.array(plaintexts, dtype="uint8")

ths = read_ths_from_ram(samples=heat_array, plaintext=plaintext_array)
container = scared.Container(ths)

attack = scared.CPAAttack(
    selection_function=scared.aes.selection_functions.encrypt.FirstSubBytes(),
    model=scared.HammingWeight(),
    discriminant=scared.maxabs,
)

attack.run(container)

# scores is (256 candidates, 16 key bytes)
key = numpy.abs(attack.scores).argmax(axis=0)

print("recovered key: ", bytes(key.tolist()).hex())
