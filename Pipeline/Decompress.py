import struct 
import json
import subprocess
import argparse
import os

def load_settings():
    with open("compression_meta.json", "r") as f:
        return json.load(f)

settings = load_settings()
vocab_file = settings['vocab_file']
bin_file = settings['bin_file']
input_f = settings['original_filename']
com = settings['compressed_file']

def decompress_pipeline(input_file, output_file):
  command = [
    "python",
    "Reference-arithmetic-coding/python/arithmetic-decompress.py",
    input_file,
    bin_file
  ]

  print("Decompressing...")

  subprocess.run(command)

  def translate_ids_to_dna(token_bin_file, vocab_file, output_dna_file):
    with open(vocab_file, 'r') as f:
        data = json.load(f)
        id_to_token = {v: k for k, v in data['model']['vocab'].items()}
        for token_info in data.get('added_tokens', []):
          id_to_token[token_info['id']] = token_info['content']

    with open(token_bin_file, 'rb') as f:
        binary_data = f.read()
    
    num_integers = len(binary_data) // 2
    ids = struct.unpack('<' + 'H' * num_integers, binary_data)
    
    for i in ids:
        if i not in id_to_token:
            print(f"CRASH FOUND: ID {i} exists in binary but not in vocab!")
            break
    reconstructed_dna = "".join([id_to_token[i] for i in ids])
    
    with open(output_dna_file, 'w') as f:
        f.write(reconstructed_dna)
        
    print(f"Success! Reconstructed {len(reconstructed_dna)} DNA bases.")
  translate_ids_to_dna(bin_file, vocab_file, output_file)

  def get_dna_only(filename):
      with open(filename, 'r') as f:
          # Keep only A, T, G, C
          return "".join([c for c in f.read().upper() if c in 'ATGC'])

  original = get_dna_only(input_f)
  reconstructed = get_dna_only(output_file)

  print(f"Match status: {original == reconstructed}")
  print(f"Lengths: {len(original)} vs {len(reconstructed)}")

def main():
  parser = argparse.ArgumentParser(description="DNA Decompression Pipeline")
  parser.add_argument("input_file")
  parser.add_argument("output_file")
  args = parser.parse_args()
  decompress_pipeline(args.input_file, args.output_file)

main()
