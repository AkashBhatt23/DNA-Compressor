import argparse
import subprocess
import os
import json
import glob
  
def run_pipeline(input_file, output_file, vocab_size):
  base_name = os.path.splitext(input_file)[0]
  bpe_output_base = f"{base_name}"
    
  print("Running BPE Tokenization...")
  subprocess.run([
      "./dnaBPE/bin/bpe.v6.exe", 
      input_file, 
      bpe_output_base, 
      "fasta", 
      str(vocab_size), 
      "4"
  ], check=True)

  vocab_files = glob.glob(f"{bpe_output_base}*.json")
  bpe_files = glob.glob(f"{bpe_output_base}*.bpe")

  if not vocab_files or not bpe_files:
      print("Error: Files not created. Check your BPE tool.")
      return

  vocab_file = vocab_files[0]
  bpe_file = bpe_files[0]
  temp_tokens = f"{base_name}_tokens.bin"

  metadata = {
  "original_filename": input_file,
  "vocab_size": vocab_size,
  "vocab_file": vocab_files[0],
  "compressed_file": output_file,
  "bin_file": temp_tokens
  }

  with open("compression_meta.json", "w") as f:
    json.dump(metadata, f)

  def translate_bpe_to_ids(bpe_file, vocab_file, output_file):
    with open(vocab_file, 'r') as f:
      data = json.load(f)
      vocab = data['model']['vocab']
    with open(bpe_file, 'r') as f:
      tokens = f.read().split();
    encoded_ids = [vocab.get(t, 0) for t in tokens]
    import struct 
    with open(output_file, 'wb') as f:
      for id_val in encoded_ids:
        f.write(struct.pack('H', id_val))

    print(f"Converted {len(encoded_ids)} tokens to binary IDs")

  translate_bpe_to_ids(bpe_file, vocab_file, temp_tokens)

  command = [
    "python",
    "Reference-arithmetic-coding/python/arithmetic-compress.py",
    temp_tokens,
    output_file
  ]

  print("Compressing...")

  subprocess.run(command)

  print("Compression Successful!")

  original = os.path.getsize(input_file)
  compressed = os.path.getsize(output_file)

  print(f"Original: {original} bytes")
  print(f"Compressed: {compressed} bytes")
  print(f"Compression ratio: {original/compressed:.2f}x")

def main():
  parser = argparse.ArgumentParser(description="DNA Compression Pipeline")
  parser.add_argument("input_file")
  parser.add_argument("output_file")
  parser.add_argument("--vocab",type = int, default = 1000)
  args = parser.parse_args()
  run_pipeline(args.input_file, args.output_file,args.vocab)

main()





