import time
import os
from bitstring import BitArray

class huffmanTree(object):
    """
    This class is able to create huffman tree nodes and assign them their parent and child
    """
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    # Overrides how the object is printed when using print(object)
    def __str__(self):
        return "{0} {1}".format(self.left, self.right)

    def nodes(self):
        return (self.left, self.right)

    def children(self):
        return (self.left, self.right)


def open_file(file: str) -> str:
    """
    This functions opens the file the user wants and returns it as a string
    :param file: path of file
    :return: file in string type
    """
    with open(file, encoding="utf-8") as file_decompressed:
        return file_decompressed.read()

def huffman_code_tree(node, code = '', left = True) -> dict:
    """
    This function creates a dictionary with the huffman tree by going from the root node of the tree all the way to its bottom
    It checks if a node is on the left of the tree which is a sign that you don't go down that node anymore by setting the parameter left
    to True. The nodes that are on the right of the tree you can go down so you set parameter left to False
    :param node: huffman tree node
    :param code: bit code
    :param left: boolean that says where the node is on the tree. If true node is on the left, if false it's on the right
    :return:
    """
    # When you go down the tree you retrieve the individual character that will be on a left part of the tree
    if type(node) is str:
        return {node: code}
    (l, r) = node.children()

    huffman_codes = {}
    huffman_codes.update(huffman_code_tree(l, code + '0', True))
    huffman_codes.update(huffman_code_tree(r, code + '1', False))

    return huffman_codes

def get_codes(str_file):
    """
    This function finds the frequency of each character in a string and then
    :param str_file: text file we want to compress in string type
    :return: Dictionary with the characters and theirs respective bits
    """
    freq_list = {}

    # If the key exists in the dictionary it will add 1 and if it doesn't exist it will create that key and assign it value 1
    for char in str_file:
        if char in freq_list:
            freq_list[char] += 1
        else:
            freq_list[char] = 1

    #This bit of code sorts the list from most frequent on the left and least frequent on the right
    freq_list = sorted(freq_list.items(), key=lambda x: x[1], reverse=True)

    nodes = freq_list

    # Through this loop we are able to find the root of the huffman tree
    while len(nodes) > 1:
        (key1, freq1) = nodes[-1]
        (key2, freq2) = nodes[-2]
        nodes = nodes[:-2]
        node = huffmanTree(key1, key2)
        nodes.append((node, freq1 + freq2))

        nodes = sorted(nodes, key=lambda x: x[1], reverse=True)

    root_node = nodes[0][0]

    huffman_codes = huffman_code_tree(root_node)

    # Print Huffman codes
    print(' Char: Huffman code\n')
    for char in huffman_codes:
        print(' %-8r: %12s' % (char, huffman_codes[char]))

    return huffman_codes

def encode_text_into_bits(huffman_codes: dict, str_file: str) -> str:
    """
    This function replaces the characters in the string with their respective bits
    :param huffman_codes: the huffman codes dictionary
    :param str_file: file in string ype
    :return: file string in bits
    """
    bit_table = str_file.maketrans(huffman_codes)

    encoded_text =  str_file.translate(bit_table)

    pad = 8 - (len(encoded_text) % 8)

    txt = encoded_text.ljust(len(encoded_text) + pad, '0')

    data_pad = "{0:08b}".format(pad)

    encoded = data_pad + txt

    return encoded

def create_compressed_file(huffman_codes: dict, str_file: str, file_path: str):
    """
    This function is responsible for taking the huffman codes and the text file in string type and sends them to be encoded in encode_text_into_bits and then through a bit array puts them in a compressed bin file
    :param huffman_codes: Dictionary with the characters and theirs respective bits
    :param str_file: text file in string type
    :param file_path: name of file to compress
    :return: string of name of compressed file
    """

    # Create file name after compression
    file_compressed_name = os.path.splitext(file_path)[0] + ".bin"

    padded_encoded_text = encode_text_into_bits(huffman_codes, str_file)

    bit_text = BitArray(bin=padded_encoded_text)

    with open(file_compressed_name, 'wb') as compressed_file:
        bit_text.tofile(compressed_file)

    return file_compressed_name

def decode_bits_into_text(huffman_codes: dict,str_bit: str):
    """
    This function turns the encoded bits into text again
    :param huffman_codes: Dictionary with the characters and theirs respective bits
    :param str_bit: the text file in bits after being encoded
    :return: string of the text decoded
    """

    pad_info = str_bit[:8]
    pad_extra = int(pad_info, 2)

    str_bit = str_bit[8:]

    encoded_text = str_bit[:-1 * pad_extra]

    code = ""
    decoded = ""

    char_code_swap = dict((code, char) for char, code in huffman_codes.items())

    for bit in encoded_text:
        code += bit
        if code in char_code_swap:
            decoded += char_code_swap[code]
            code = ""

    return decoded

def create_decompressed_file(huffman_codes: dict, compressed_file: str):
    """
    This function creates the decompressed file by taking the huffman code and the previously compressed file and turning them back into the original text file
    :param huffman_codes: Dictionary with the characters and theirs respective bits
    :param compressed_file: name of file to compress
    :return:
    """
    # Create file name after decompression
    file_decompressed_name = os.path.splitext(compressed_file)[0] + "_decompressed.txt"

    with open(compressed_file, 'rb') as file_compressed:
        num_byte = file_compressed.read(1)
        str_bit = ""

        while len(num_byte) > 0:
            num_byte = ord(num_byte)

            bits = bin(num_byte)[2:].rjust(8, '0')

            str_bit += bits

            num_byte = file_compressed.read(1)
        str_decoded = decode_bits_into_text(huffman_codes,str_bit)

    with open(file_decompressed_name, 'w', encoding= "utf-8") as file_decompressed:
        file_decompressed.write(str_decoded)

if __name__ == '__main__':
    start = time.time()

    file_to_compress = 'book_little_folks.txt'
    str_file = open_file(file_to_compress)

    huffman_codes = get_codes(str_file)

    compressed_file = create_compressed_file(huffman_codes, str_file, file_to_compress)
    decompressed_file = create_decompressed_file(huffman_codes, compressed_file)

    original_size = os.path.getsize(file_to_compress);
    compression_size = os.path.getsize(os.path.splitext(file_to_compress)[0] + '.bin')
    decompression_size = os.path.getsize(os.path.splitext(compressed_file)[0] + '_decompressed.txt')

    compression_ratio = (original_size - compression_size) / original_size * 100

    print("Program took about {0:.2f} seconds to compress and decompress the file\n".format(time.time() - start))
    print("The original file has been reduced in size by {0:.2f}%.\n".format(compression_ratio))
    print("The lossless compression works since the decompressed file, {0}KB has equal size to the file before compression, {1}KB.".format(decompression_size,original_size))