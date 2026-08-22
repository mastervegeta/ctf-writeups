import pathlib

import numpy
import scared
from estraces import read_ths_from_ram


def open_files_and_get_data():
    """Each traces/traceNN.txt is:

        Plaintext: <32 hex chars>
        Power trace: [41, 63, 94, ...]
    """
    folder = pathlib.Path("traces")

    heat_data = []
    plaintexts = []

    for file in sorted(folder.iterdir()):
        if not file.is_file():
            continue

        data = file.read_text()
        plaintext_data, powerdata = data.split("Power trace: ")

        plaintext = plaintext_data.split(": ")[1].strip()
        power_list = [int(x) for x in powerdata.strip().strip("[").strip("]").split(", ")]

        plaintexts.append(plaintext)
        heat_data.append(power_list)

    return heat_data, plaintexts


def turn_hexlist_into_list_of_ints(list_of_hexes):
    list_of_list_of_ints = []
    for hexer in list_of_hexes:
        byted_hexes = bytes.fromhex(hexer)
        list_of_ints = [int(byte) for byte in byted_hexes]
        list_of_list_of_ints.append(list_of_ints)
    return list_of_list_of_ints


heat_data, plaintexts = open_files_and_get_data()
plaintexts = turn_hexlist_into_list_of_ints(plaintexts)

heat_array = numpy.array(heat_data, dtype="float32")
plaintext_array = numpy.array(plaintexts, dtype="uint8")

# identical to Part 1 from here down
ths = read_ths_from_ram(samples=heat_array, plaintext=plaintext_array)
container = scared.Container(ths)

attack = scared.CPAAttack(
    selection_function=scared.aes.selection_functions.encrypt.FirstSubBytes(),
    model=scared.HammingWeight(),
    discriminant=scared.maxabs,
)

attack.run(container)

key = numpy.abs(attack.scores).argmax(axis=0)

print("recovered key: ", bytes(key.tolist()).hex())
