import os
import subprocess
import argparse
import time
from glob import glob

# Function to concatenate FASTA files
def concatenate_files(input_folder, output_name):
    """Concatenate all FASTA files in a folder into a single file."""
    concatenated_file = f'{output_name}_concatenated_{int(time.time())}.fasta'

    with open(concatenated_file, 'w') as f:
        for file in glob(os.path.join(input_folder, '*.fasta')):
            with open(file, 'r') as fasta_file:
                f.write(fasta_file.read())

    print(f"Finished concatenating all FASTA files in {input_folder} into {concatenated_file}")

    return concatenated_file

# Function to build Bowtie2 index
def build_index(input_file, output_name, threads):
    """Build Bowtie2 index from a FASTA file."""
    process = subprocess.Popen(['bowtie2-build', '--threads', str(threads), input_file, output_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Print output from the process in real time
    while True:
        output = process.stdout.readline()

        if output == '' and process.poll() is not None:
            break

        if output:
            print(output.strip())

    if process.returncode != 0:
        print(f"Error building Bowtie2 index: {process.stderr.read().strip()}")
        return False

    return True

# Main function to handle command-line arguments and call other functions
def main():
    # Handle command-line arguments
    parser = argparse.ArgumentParser(description='Build Bowtie2 index from multiple FASTA files.')
    parser.add_argument('--input', required=True, help='Input folder with FASTA files.')
    parser.add_argument('--output', required=True, help='Output name for Bowtie2 index.')
    parser.add_argument('--threads', type=int, default=1, help='Number of threads for Bowtie2.')
    args = parser.parse_args()

    # Concatenate the FASTA files
    concatenated_file = concatenate_files(args.input, args.output)

    # Build the Bowtie2 index
    if build_index(concatenated_file, args.output, args.threads):
        print(f"Successfully built Bowtie2 index: {args.output}")

    # Delete the temporary concatenated file
    os.remove(concatenated_file)

if __name__ == '__main__':
    main()

