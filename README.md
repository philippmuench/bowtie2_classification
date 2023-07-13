# Genome Alignment Scripts
These scripts are used for aligning FASTA formatted sequences against multiple indexed databases using the Bowtie2 tool. The alignment is performed on a sliding window of sequences.

## Requirements
Python 3.6 or above
Biopython, bowtie2, pysam which can be installed via:

```
conda install -c bioconda bowtie2
conda install -c bioconda pysam
```

## Usage

### Step 1: Index your database
Before starting the alignment, you must first index your database using the create_database.py script.

```
python create_database.py --input input_folder --output database_name --threads num_threads
```

- `input_folder` is a folder containing FASTA formatted files.
- `database_name` is the name of the database to be created.
- `num_threads` is the number of threads to be used by Bowtie2. Optional, default is 1.

## Step 2: Perform the alignment
After your databases are indexed, you can perform the alignment using the align.py script.

```
python align.py --input input_directory --databases db1 db2 db3 --threads num_threads --stride stride --window_size window_size --relaxed --output output_file
```

- `input_directory` is the directory containing the FASTA files to be aligned.
- `db1` `db2` `db3` are the Bowtie2 indexed databases. Multiple databases can be provided.
- `num_threads` is the number of threads to be used by Bowtie2. Optional, default is 1.
- `stride` is the step size for the sliding window. Optional, default is 150.
- `window_size` is the window size for the sliding window. Optional, default is 150.
- `--relaxed` is an optional flag that, if set, relaxes the alignment constraints.
- `output_file` is the name of the output file that will store the alignment results. Optional, default is 'alignment_report.csv'.

## Output
The alignment script outputs alignment statistics both to the console and to a CSV file.

For example, running the script may output the following to the console:

```
Alignments of worm.fasta: group1 (100482 / 67.0% alignments); group2 (49810 / 33.0% alignments)
Alignments of yeast.fasta: group1 (81036 / 54.0% alignments); group2 (69152 / 46.0% alignments)
Database with most alignments overall: group1 (181518 / 60.5% alignments)
```

In addition, a CSV file is generated with alignment details for each file. The columns of the file are:

- filename: the name of the FASTA file.
- The name of each database: the number of successful alignments to this database.

## Troubleshooting
- If an error occurs, check the `alignment.log` file that is generated during script execution. This file contains detailed logging information that may help identify the issue.

## Tutorial

We have very small example files in the `bacteria_database/` and `virus_database/` folder. So we can create two bowtie2 databases:

```
python create_db.py --input bacteria_database --output bacteria_database --threads 1
python create_db.py --input virus_database --output virus_database --threads 1
```

We want to query the file in the `input/` folder and test if there are hits 

```
python align.py --input input_files --databases virus_database bacteria_database --threads 1
```

the output will be written to the screen

```
Alignments of worm.fasta: virus_database (0 / 0.00% alignments); bacteria_database (0 / 0.00% alignments)
Alignments of yeast.fasta: virus_database (0 / 0.00% alignments); bacteria_database (0 / 0.00% alignments)

Database with most alignments overall: virus_database (0 / 0.00% alignments)
```
