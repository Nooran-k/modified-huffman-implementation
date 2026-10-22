import json

RAW_BITS = 8

def decompress(compressed_path, output_path):
    with open(compressed_path, "rb") as f:
        raw = f.read()

    # 1. split the header (first line) from the payload (the packed bits)
    header_line, payload = raw.split(b"\n", 1)
    header = json.loads(header_line)
    table, pad, length = header["table"], header["pad"], header["length"]

    # 2. turn the payload bytes into a string of 0s and 1s, remove the padding
    bits = "".join(format(b, "08b") for b in payload)
    if pad:
        bits = bits[:-pad]

    # 3. decode: read bit by bit until the bits match a code in the table
    decode = {code: sym for sym, code in table.items()}
    out = []
    current = ""
    i = 0
    while len(out) < length:
        current += bits[i]
        i += 1
        if current in decode:
            sym = decode[current]
            if sym == "Others":      # rare character: the next 16 bits are the character itself
                out.append(chr(int(bits[i:i + RAW_BITS], 2)))
                i += RAW_BITS
            else:
                out.append(sym)
            current = ""

    # 4. write the recovered text
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(out))