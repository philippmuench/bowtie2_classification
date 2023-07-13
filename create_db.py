import os
import subprocess
import argparse
from glob import glob

# Function to concatenate FASTA files
def concatenate_files(input_folder):
    """Concatenate all FASTA files in a folder into a single file."""
    concatenated_file = 'concatenated.fasta'

    with open(concatenated_file, 'w') as f:
        for file in glob(os.path.join(input_folder, '*.fasta')):
            with open(file, 'r') as fasta_file:
                f.write(fasta_file.read())

    return concatenated_file

# Function to build Bowtie2 index
def build_index(input_file, output_name, threads):
    """Build Bowtie2 index from a FASTA file."""
    result = subprocess.run(['bowtie2-build', '--threads', str(threads), input_file, output_name], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error building Bowtie2 index: {result.stderr}")
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
    concatenated_file = concatenate_files(args.input)

    # Build the Bowtie2 index
    if build_index(concatenated_file, args.output, args.threads):
        print(f"Successfully built Bowtie2 index: {args.output}")

    # Delete the temporary concatenated file
    os.remove(concatenated_file)

if __name__ == '__main__':
    main()

