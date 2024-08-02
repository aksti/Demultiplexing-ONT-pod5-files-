import os
import csv
import argparse
import pod5
from uuid import UUID
from concurrent.futures import ProcessPoolExecutor, as_completed
import tempfile
import shutil
import uuid

def extract_ids_from_fastq(fastq_file):
    ids = []
    with open(fastq_file, 'r') as file:
        while True:
            id_line = file.readline()
            if not id_line:
                break
            id = id_line.strip().split('\t')[0][1:]  # remove the '@' character and split at tab
            ids.append(id)
            file.readline()
            file.readline()
            file.readline()
    return ids

def write_ids_to_csv(ids, csv_file):
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        for id in ids:
            writer.writerow([id])

def extract_ids_from_pod5(pod5_file):
    ids = []
    with pod5.Reader(pod5_file) as reader:
        for record in reader:
            ids.append(str(record.read_id))
    return ids

def extract_matching_ids(matching_csv):
    matching_dict = {}
    with open(matching_csv, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header
        for row in reader:
            pod5_file = row[0]
            fastq_file = row[1]
            id = row[2]
            if fastq_file not in matching_dict:
                matching_dict[fastq_file] = []
            matching_dict[fastq_file].append((pod5_file, id))
    return matching_dict

def filter_and_write_pod5(input_pod5_files, ids, output_pod5_file):
    try:
        with pod5.Writer(output_pod5_file) as writer:
            for input_pod5_file in input_pod5_files:
                with pod5.Reader(input_pod5_file) as reader:
                    for record in reader:
                        if str(record.read_id) in ids:
                            writer.add_read(record.to_read())
    except Exception as e:
        print(f"Failed to process {input_pod5_file}: {e}")

def process_files(input_fastq_dir, input_pod5_dir, output_csv, output_pod5_dir, threads):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_tmp_dir = os.path.join(script_dir, '.csv-tmp')
    if not os.path.exists(csv_tmp_dir):
        os.makedirs(csv_tmp_dir)

    fastq_files = [f for f in os.listdir(input_fastq_dir) if f.endswith('.fastq')]
    pod5_files = [f for f in os.listdir(input_pod5_dir) if f.endswith('.pod5')]

    # Extract IDs from FASTQ files and save to CSV
    fastq_ids_dict = {}
    for fastq_file in fastq_files:
        fastq_file_path = os.path.join(input_fastq_dir, fastq_file)
        fastq_ids = extract_ids_from_fastq(fastq_file_path)
        csv_file = os.path.join(csv_tmp_dir, f"{fastq_file}.csv")
        write_ids_to_csv(fastq_ids, csv_file)
        fastq_ids_dict[fastq_file] = fastq_ids

    # Extract IDs from POD5 files and save to CSV
    pod5_ids_dict = {}
    for pod5_file in pod5_files:
        pod5_file_path = os.path.join(input_pod5_dir, pod5_file)
        pod5_ids = extract_ids_from_pod5(pod5_file_path)
        csv_file = os.path.join(csv_tmp_dir, f"{pod5_file}.csv")
        write_ids_to_csv(pod5_ids, csv_file)
        pod5_ids_dict[pod5_file] = pod5_ids

    # Match IDs and create matching CSV
    with open(output_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['POD5 File', 'FASTQ File', 'ID'])
        for fastq_file, fastq_ids in fastq_ids_dict.items():
            for pod5_file, pod5_ids in pod5_ids_dict.items():
                common_ids = set(fastq_ids).intersection(pod5_ids)
                for common_id in common_ids:
                    writer.writerow([pod5_file, fastq_file, common_id])

    # Filter and write new POD5 files
    matching_dict = extract_matching_ids(output_csv)
    if not os.path.exists(output_pod5_dir):
        os.makedirs(output_pod5_dir)

    with ProcessPoolExecutor(max_workers=threads) as executor:
        future_to_file = {}
        for fastq_file, matches in matching_dict.items():
            output_pod5_file = os.path.join(output_pod5_dir, fastq_file.replace('.fastq', '.pod5'))
            input_pod5_files = list(set([os.path.join(input_pod5_dir, pod5_file) for pod5_file, _ in matches]))
            ids = {id for _, id in matches}

            future = executor.submit(filter_and_write_pod5, input_pod5_files, ids, output_pod5_file)
            future_to_file[future] = (input_pod5_files, output_pod5_file)

        for future in as_completed(future_to_file):
            input_pod5_files, output_pod5_file = future_to_file[future]
            try:
                future.result()
                print(f"Created new POD5 file: {output_pod5_file}")
            except Exception as e:
                print(f"Failed to create POD5 file {output_pod5_file} from {input_pod5_files}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract IDs from FASTQ and POD5 files, match them, and create new filtered POD5 files.")
    parser.add_argument("--fastq", required=True, help="Directory containing FASTQ files.")
    parser.add_argument("--pod5", required=True, help="Directory containing original POD5 files.")
    parser.add_argument("--output_csv", required=True, help="Output CSV file to save the matching IDs.")
    parser.add_argument("--output_pod5", required=True, help="Directory to save new filtered POD5 files.")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use for processing.")
    
    args = parser.parse_args()
    
    process_files(args.fastq, args.pod5, args.output_csv, args.output_pod5, args.threads)

if __name__ == "__main__":
    main()
