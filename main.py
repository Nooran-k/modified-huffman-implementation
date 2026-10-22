from implementation import build_modified_code_table
from compression import compress
from decompression import decompress
import os

input_file = input("Input file name: ")
min_limit = float(input("Minimum probability (e.g. 0.05): "))
compressed_file = input("Compressed file name: ")
output_file = input("Decompressed file name: ")

table = build_modified_code_table(input_file, min_limit)
compress(input_file, compressed_file, table)
decompress(compressed_file, output_file)

#calc compressed size 
original_size = os.path.getsize(input_file)
compressed_size = os.path.getsize(compressed_file)

# the header is everything before the first newline; the rest is the packed bits
data = open(compressed_file, "rb").read()
payload_size = len(data.split(b"\n", 1)[1])

print(f"Compressed data only: {payload_size / original_size * 100:.1f}% of the original size")
print(f"Whole file (with code table): {compressed_size / original_size * 100:.1f}% of the original size")
print("Done. Recovered file saved to", output_file)