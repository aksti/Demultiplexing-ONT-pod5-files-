# POD5 and FASTQ ID Matching and Filtering

This repository contains a Python script designed to streamline the process of matching IDs between FASTQ and POD5 files, and creating filtered POD5 files based on these matches.

## Features:
- Extracts IDs from FASTQ and POD5 files.
- Matches IDs between FASTQ and POD5 files and generates a matching CSV file.
- Filters and creates new POD5 files containing only the matched IDs.
- Utilizes multi-threading for improved performance.
- Stores temporary CSV files in a dedicated `.csv-tmp` directory.

## Installation:
1. Ensure you have Python 3 installed.
2. Install the `pod5` package using pip:
   ```bash
   pip install pod5
   ```
   For more details, visit the [POD5 package page on PyPI](https://pypi.org/project/pod5/).

## Usage:
1. Ensure the `pod5` package is installed.
2. Run the script with the appropriate arguments:
   ```bash
   python3 demux_pod5.py --fastq <fastq_directory> --pod5 <pod5_directory> --output_csv <output_csv_file> --output_pod5 <output_pod5_directory> --threads <number_of_threads>
   ```

  Arguments:
    --fastq", required=True, help="Directory containing FASTQ files
    --pod5", required=True, help="Directory containing original POD5 files
    --output_csv", required=True, help="Output CSV file to save the matching IDs
    --output_pod5", required=True, help="Directory to save new filtered POD5 files
    --threads", type=int, default=4, help="Number of threads to use for processing

## Requirements:
- Python 3.6+
- `pod5` package
