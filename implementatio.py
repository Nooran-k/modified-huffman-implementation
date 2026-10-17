import os

# We create a simple class to represent each node in the Huffman Tree.
# Each symbol will be a leaf node in the tree.
class HuffmanNode:
    def __init__(self, symbol, probability):
        self.symbol = symbol              # The character (e.g., 'a') or "Others"
        self.probability = probability    # The probability value
        self.left = None                  # Left branch (assigned 0)
        self.right = None                 # Right branch (assigned 1)

# Helper function to sort our list of nodes by probability
def get_node_probability(node):
    return node.probability

def build_modified_code_table(input_path, min_limit):
    """
    Reads text, calculates probabilities, groups rare symbols into "Others",
    and builds the Huffman code table.
    """
    # 1. Read the input file
    if not os.path.exists(input_path):
        print("Error: The file was not found.")
        return {}
        
    file = open(input_path, 'r')
    text_data = file.read()
    file.close()
    
    if len(text_data) == 0:
        print("Error: The file is empty.")
        return {}

    # 2. Count the frequency of each character
    frequencies = {}
    for char in text_data:
        if char in frequencies:
            frequencies[char] = frequencies[char] + 1
        else:
            frequencies[char] = 1
            
    # 3. Calculate probabilities (frequency divided by total characters)
    total_chars = len(text_data)
    probabilities = {}
    for char in frequencies:
        probabilities[char] = frequencies[char] / total_chars

    # 4. Apply Modified Huffman rules
    # Symbols with Probabilities <= the Limit will be grouped in one group called "Others".
    modified_probs = {}
    others_probability_sum = 0.0
    
    for char in probabilities:
        prob = probabilities[char]
        if prob <= min_limit:
            others_probability_sum = others_probability_sum + prob
        else:
            modified_probs[char] = prob
            
    # If we found any rare characters, add the "Others" group to our dictionary
    if others_probability_sum > 0:
        modified_probs["Others"] = others_probability_sum

    # 5. Prepare the nodes for the tree
    nodes_list = []
    for symbol in modified_probs:
        new_node = HuffmanNode(symbol, modified_probs[symbol])
        nodes_list.append(new_node)
        
    # Handle the edge case where the file only has one type of valid symbol
    if len(nodes_list) == 1:
        single_symbol = nodes_list[0].symbol
        return {single_symbol: "0"}

    # 6. Build the Huffman Tree
    # Continue this process till all symbols merged into one root node.
    while len(nodes_list) > 1:
        # Sort the list from Highest to Lowest probability
        nodes_list.sort(key=get_node_probability, reverse=True)
        
        # Combining the two symbols or composite symbols with the least probabilities.
        right_node = nodes_list.pop() 
        left_node = nodes_list.pop()
        
        # Form a new parent composite symbol, which has the combined probabilities.
        combined_prob = left_node.probability + right_node.probability
        parent_node = HuffmanNode(symbol=None, probability=combined_prob)
        
        # Assign a bit 0 and 1 to the two links.
        parent_node.left = left_node
        parent_node.right = right_node
        
        # Put the new parent node back into our list
        nodes_list.append(parent_node)
        
    # The last remaining node is the root of our entire tree
    root_node = nodes_list[0]
    
    # 7. Generate the binary codes by walking down the tree
    code_table = {}
    
    def generate_codes(node, current_binary_string):
        if node is None:
            return
            
        # For each symbol, the sequence of the 0s and 1s from the root node to the symbol is the code word.
        if node.symbol is not None:
            code_table[node.symbol] = current_binary_string
            return
            
        generate_codes(node.left, current_binary_string + "0")
        generate_codes(node.right, current_binary_string + "1")
        
    generate_codes(root_node, "")
    
    return code_table

# ==========================================
# LECTURE EXAMPLE TEST BLOCK
# ==========================================
if __name__ == "__main__":
    test_file_name = "lecture_test.txt"
    lecture_string = "abcazdafcqdadcuabapd" 
    
    file = open(test_file_name, 'w')
    file.write(lecture_string)
    file.close()
    
    # Run the function with the limit of 0.05
    # Symbols with probability <= 0.05 (f, z, q, p, u) will become "Others"
    print("Testing Lecture Example...")
    final_table = build_modified_code_table(test_file_name, min_limit=0.05)
    
    # Print the results
    for symbol in final_table:
        binary_code = final_table[symbol]
        print(f"Symbol: {symbol} --> Code: {binary_code}")