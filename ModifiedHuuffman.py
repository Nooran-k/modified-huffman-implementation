import os
import json

# ==========================================
# CONSTANTS
# ==========================================
# The exact number of bits we will use to store a rare character
RAW_BITS = 16 

# ==========================================
# TEAMMATE 1: PROBABILITY & TABLE GENERATION
# ==========================================
class HuffmanNode:
    def __init__(self, symbol, probability):
        self.symbol = symbol              
        self.probability = probability    
        self.left = None                  
        self.right = None                 

def get_node_probability(node):
    return node.probability

def build_modified_code_table(input_path, min_limit):
    """
    Reads text, calculates probabilities, groups rare symbols into "Others",
    and builds the Huffman code table.
    """
    if not os.path.exists(input_path):
        print("Error: The file was not found.")
        return {}
        
    file = open(input_path, 'r', encoding='utf-8')
    text_data = file.read()
    file.close()
    
    if len(text_data) == 0:
        print("Error: The file is empty.")
        return {}

    # Count the frequency of each character
    frequencies = {}
    for char in text_data:
        if char in frequencies:
            frequencies[char] = frequencies[char] + 1
        else:
            frequencies[char] = 1
            
    # Calculate probabilities
    total_chars = len(text_data)
    probabilities = {}
    for char in frequencies:
        probabilities[char] = frequencies[char] / total_chars

    # Apply Modified Huffman rules (group rare symbols into "Others")
    modified_probs = {}
    others_probability_sum = 0.0
    
    for char in probabilities:
        prob = probabilities[char]
        if prob <= min_limit:
            others_probability_sum = others_probability_sum + prob
        else:
            modified_probs[char] = prob
            
    if others_probability_sum > 0:
        modified_probs["Others"] = others_probability_sum

    # Prepare nodes for the tree
    nodes_list = []
    for symbol in modified_probs:
        new_node = HuffmanNode(symbol, modified_probs[symbol])
        nodes_list.append(new_node)
        
    if len(nodes_list) == 1:
        return {nodes_list[0].symbol: "0"}

    # Build the Huffman Tree
    while len(nodes_list) > 1:
        nodes_list.sort(key=get_node_probability, reverse=True)
        
        right_node = nodes_list.pop() 
        left_node = nodes_list.pop()
        
        combined_prob = left_node.probability + right_node.probability
        parent_node = HuffmanNode(symbol=None, probability=combined_prob)
        
        parent_node.left = left_node
        parent_node.right = right_node
        
        nodes_list.append(parent_node)
        
    root_node = nodes_list[0]
    code_table = {}
    
    def generate_codes(node, current_binary_string):
        if node is None:
            return
        if node.symbol is not None:
            code_table[node.symbol] = current_binary_string
            return
            
        generate_codes(node.left, current_binary_string + "0")
        generate_codes(node.right, current_binary_string + "1")
        
    generate_codes(root_node, "")
    return code_table


# ==========================================
# TEAMMATE 2: COMPRESSION
# ==========================================
def compress(input_path, output_path, code_table):
    """
    Reads original text, translates it to 0s and 1s using Teammate 1's table,
    and saves it as a packed binary file with a JSON header.
    """
    if not os.path.exists(input_path):
        print("Error: Input file not found.")
        return
        
    file = open(input_path, "r", encoding="utf-8")
    text = file.read()
    file.close()

    # Translate text into '0's and '1's
    bit_string = ""
    for char in text:
        if char in code_table:
            bit_string = bit_string + code_table[char]
        else:
            # Rare character: Add "Others" code, then 16-bit binary of character
            bit_string = bit_string + code_table["Others"]
            char_number = ord(char)
            char_binary = format(char_number, "016b")
            bit_string = bit_string + char_binary

    # Calculate padding
    remainder = len(bit_string) % 8
    if remainder == 0:
        pad_length = 0
    else:
        pad_length = 8 - remainder
        
    for i in range(pad_length):
        bit_string = bit_string + "0"

    # Pack bits into bytes
    byte_list = []
    i = 0
    while i < len(bit_string):
        byte_chunk = bit_string[i : i + 8]
        byte_value = int(byte_chunk, 2)
        byte_list.append(byte_value)
        i = i + 8
        
    payload_bytes = bytes(byte_list)

    # Create header
    header_dict = {
        "table": code_table,
        "pad": pad_length,
        "length": len(text)
    }
    header_json = json.dumps(header_dict)
    header_bytes = header_json.encode("utf-8")

    # Write to output file
    out_file = open(output_path, "wb")
    out_file.write(header_bytes)
    out_file.write(b"\n") 
    out_file.write(payload_bytes)
    out_file.close()


# ==========================================
# TEAMMATE 3: DECOMPRESSION
# ==========================================
def decompress(compressed_path, output_path):
    """
    Reads compressed binary file, uses JSON header to rebuild table,
    and translates 0s and 1s back into original text.
    """
    if not os.path.exists(compressed_path):
        print("Error: Compressed file not found.")
        return

    file = open(compressed_path, "rb")
    raw_data = file.read()
    file.close()

    # Split header from payload
    parts = raw_data.split(b"\n", 1)
    header_line = parts[0]
    payload = parts[1]

    # Parse header
    header = json.loads(header_line)
    code_table = header["table"]
    pad_length = header["pad"]
    text_length = header["length"]

    # Unpack payload into bit string
    bit_string = ""
    for byte in payload:
        binary_chunk = format(byte, "08b")
        bit_string = bit_string + binary_chunk

    if pad_length > 0:
        bit_string = bit_string[:-pad_length]

    # Reverse table for decoding
    decode_table = {}
    for symbol in code_table:
        binary_code = code_table[symbol]
        decode_table[binary_code] = symbol

    # Decode bit string
    output_text = ""
    current_bits = ""
    i = 0
    
    while len(output_text) < text_length:
        current_bits = current_bits + bit_string[i]
        i = i + 1
        
        if current_bits in decode_table:
            symbol = decode_table[current_bits]
            
            if symbol == "Others":
                rare_bits = bit_string[i : i + RAW_BITS]
                rare_char = chr(int(rare_bits, 2))
                output_text = output_text + rare_char
                i = i + RAW_BITS
            else:
                output_text = output_text + symbol
                
            current_bits = ""

    file = open(output_path, "w", encoding="utf-8")
    file.write(output_text)
    file.close()


# ==========================================
# MAIN EXECUTION PIPELINE (TESTING)
# ==========================================
if __name__ == "__main__":
    # Setup test file using the lecture example string
    original_file = "input.txt"
    compressed_file = "compressed.bin"
    decompressed_file = "output.txt"
    
    lecture_string = "abcazdafcqdadcuabapd"
    
    file = open(original_file, "w", encoding="utf-8")
    file.write(lecture_string)
    file.close()
    
    print("--- Starting Modified Huffman Process ---")
    
    # Teammate 1
    print("\n1. Teammate 1 generating code table (Limit = 0.05)...")
    my_table = build_modified_code_table(original_file, min_limit=0.05)
    for sym in my_table:
        print(f"   Symbol: {sym} -> Code: {my_table[sym]}")
        
    # Teammate 2
    print("\n2. Teammate 2 compressing data to binary...")
    compress(original_file, compressed_file, my_table)
    print(f"   Compressed file size: {os.path.getsize(compressed_file)} bytes.")
    
    # Teammate 3
    print("\n3. Teammate 3 decompressing data...")
    decompress(compressed_file, decompressed_file)
    
    # Validation
    file = open(decompressed_file, "r", encoding="utf-8")
    recovered_text = file.read()
    file.close()
    
    print("\n--- Validation ---")
    print(f"Original Text : {lecture_string}")
    print(f"Recovered Text: {recovered_text}")
    
    if lecture_string == recovered_text:
        print("SUCCESS! The decompressed text matches the original perfectly.")
    else:
        print("FAIL! The text did not match.")