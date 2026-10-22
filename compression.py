import json
import os

RAW_BITS = 8 

def compress(input_path, output_path, code_table):
    """
    Reads the original text, translates it to 0s and 1s using Teammate 1's table,
    and saves it as a packed binary file with a JSON header.
    """
    # 1. Read the original text file
    if not os.path.exists(input_path):
        print("Error: Input file not found.")
        return
        
    file = open(input_path, "r", encoding="utf-8")
    text = file.read()
    file.close()

    if len(text) == 0:
        print("Error: File is empty.")
        return

    # 2. Translate text into a giant string of '0's and '1's
    bit_string = ""
    for char in text:
        if char in code_table:
            # It is a normal character, just add its Huffman code
            bit_string = bit_string + code_table[char]
        else:
            # It is a rare character! Add the "Others" code first
            bit_string = bit_string + code_table["Others"]
            
            # Get the raw number value of the character (its ASCII/Unicode value)
            char_number = ord(char)
            # Convert that number into a 8-bit binary string (e.g., "0000000001100001")
            char_binary = format(char_number, "08b")
            
            # Add the original symbol code right after the "Others" code
            bit_string = bit_string + char_binary

    # 3. Calculate padding
    # We must pack bits into 8-bit bytes. If our string length isn't a multiple of 8, we add zeros.
    remainder = len(bit_string) % 8
    if remainder == 0:
        pad_length = 0
    else:
        pad_length = 8 - remainder
        
    # Add the padding zeros to the end of our bit string
    for i in range(pad_length):
        bit_string = bit_string + "0"

    # 4. Pack the '0' and '1' string into actual binary bytes
    byte_list = []
    i = 0
    while i < len(bit_string):
        byte_chunk = bit_string[i : i + 8]
        byte_list.append(int(byte_chunk, 2))
        i = i + 8

    payload_bytes = bytes(byte_list)

    # 5. Write the JSON header, a newline, then the packed bytes
    header_dict = {"table": code_table, "pad": pad_length, "length": len(text)}
    header_bytes = json.dumps(header_dict, separators=(",", ":")).encode("utf-8")
    out_file = open(output_path, "wb")
    out_file.write(header_bytes)
    out_file.write(b"\n")
    out_file.write(payload_bytes)
    out_file.close()