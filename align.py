import os
import subprocess
import csv
from Bio import SeqIO
import argparse
import glob
import logging
import pysam

# Set up logging
logging.basicConfig(level=logging.INFO, filename='alignment.log')

def sliding_window(seq, window_size, step_size):
    for i in range(0, len(seq) - window_size + 1, step_size):
        yield seq[i:i+window_size]

def align_sequences(fasta_file, database, threads, relaxed):
    options = ['-x', database, '-f', fasta_file, '-S', 'alignment.sam', '--threads', str(threads)]

    if relaxed:
        options.extend(['-N', '1'])

    try:
        result = subprocess.run(['bowtie2'] + options, capture_output=True, text=True)
        result.check_returncode()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error aligning sequences with {database}: {e.stderr}")
        return 0

    # Read the sam file using pysam
    samfile = pysam.AlignmentFile('alignment.sam', 'r')

    success_count = 0
    for read in samfile:
        # Check if the alignment is successful
        if not read.is_unmapped and not read.is_secondary:
            success_count += 1

    samfile.close()

    return success_count
def create_window_file(fasta_file, window_size, step_size):
    temp_file = 'temp.fasta'
    total_windows = 0

    with open(temp_file, 'w') as f:
        for record in SeqIO.parse(fasta_file, 'fasta'):
            seq = str(record.seq)

            for i, window in enumerate(sliding_window(seq, window_size, step_size)):
                f.write(f'>temp_{i}\n{window}\n')
                total_windows += 1

    return temp_file, total_windows

def main():
    parser = argparse.ArgumentParser(description='Perform alignment of sliding windows.')
    parser.add_argument('--input', required=True, help='Input directory containing FASTA files.')
    parser.add_argument('--stride', type=int, default=150, help='Stride/Step size for sliding window.')
    parser.add_argument('--window_size', type=int, default=150, help='Window size for sliding window.')
    parser.add_argument('--databases', nargs='+', required=True, help='Bowtie2 indexed databases.')
    parser.add_argument('--threads', type=int, default=1, help='Number of threads for Bowtie2.')
    parser.add_argument('--relaxed', action='store_true', help='Relax alignment constraints.')
    parser.add_argument('--output', default='alignment_report.csv', help='Output CSV file for alignment results.')
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        logging.error(f"Input directory does not exist: {args.input}")
        return

    if args.stride <= 0 or args.window_size <= 0:
        logging.error("Stride and window size must be positive integers.")
        return

    for db in args.databases:
        if not os.path.isfile(db + ".1.bt2"):
            logging.error(f"Bowtie2 database does not exist: {db}")
            return

    all_counts = {db: 0 for db in args.databases}
    all_windows = 0

    fasta_files = glob.glob(os.path.join(args.input, '*.fasta'))

    with open(args.output, 'w', newline='') as csvfile:
        fieldnames = ['filename'] + args.databases
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for fasta_file in fasta_files:
            logging.info(f"Processing file: {fasta_file}")

            window_file, total_windows = create_window_file(fasta_file, args.window_size, args.stride)
            all_windows += total_windows

            counts = {}
            for db in args.databases:
                logging.info(f"Aligning sequences with {db}")
                counts[db] = align_sequences(window_file, db, args.threads, args.relaxed)
                all_counts[db] += counts[db]

            print(f"Alignments of {os.path.basename(fasta_file)}:", '; '.join([f"{db} ({counts[db]} / {counts[db] * 100 / total_windows:.2f}% alignments)" for db in args.databases]))

            writer.writerow({**{'filename': os.path.basename(fasta_file)}, **counts})

            logging.info(f"Finished processing file: {fasta_file}")

            os.remove(window_file)

    max_db = max(all_counts, key=all_counts.get)
    print(f"\nDatabase with most alignments overall: {max_db} ({all_counts[max_db]} / {all_counts[max_db] * 100 / all_windows:.2f}% alignments)")

if __name__ == '__main__':
    main()

