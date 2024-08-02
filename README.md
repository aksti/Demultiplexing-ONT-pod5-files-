# POD5 and FASTQ ID Matching and Filtering

This repository contains a Python script designed to streamline the process of matching IDs between FASTQ and POD5 files, and creating filtered POD5 files based on these matches. 

## Features:
- Extracts IDs from FASTQ and POD5 files.
- Matches IDs between FASTQ and POD5 files and generates a matching CSV file.
- Filters and creates new POD5 files containing only the matched IDs.
- Utilizes multi-threading for improved performance.
- Stores temporary CSV files in a dedicated `.csv-tmp` directory.

## Usage:
1. Ensure the `pod5` package is installed.
2. Run the script with the appropriate arguments:
   ```bash
   python integrated_script.py --fastq <fastq_directory> --pod5 <pod5_directory> --output_csv <output_csv_file> --output_pod5 <output_pod5_directory> --threads <number_of_threads>
   ```

## Requirements:
- Python 3.6+
- `pod5` package