'''

Data Management

This script is meant to check the integrity of the data downloaded for the scanner server in preparation to storage
and offline data analysis.

The script takes the zipped downloaded folder as input, unzip it and attempts to read all the dicom files to check data integrity
while creating a report of the acquisition protocol including the following information:

- Series Number
- Protocol Name
- Series Description
- Image Count

Note: it depends on pydicom (https://pydicom.github.io/) and was tested on Siemens IMA files (Scanner type: 7T MAGNETOM Plus,
Software version: MR_VE12U)

'''


import os, glob
import zipfile
import pydicom
import shutil
from collections import defaultdict

def check_log_file(log_file):
	"""Check if the log file already exists in the parent folder."""
	if os.path.exists(log_file):
		print(f"Log file '{log_file}' already exists. Aborting process.\n")
		return True
	return False

def unzip_folder(zip_path, extract_to):
	"""Unzips the given folder to the specified directory."""
	with zipfile.ZipFile(zip_path, 'r') as zip_ref:
		zip_ref.extractall(extract_to)

def process_dicom_files(folder_path):
	"""Processes DICOM files and logs count per SeriesNumber, ProtocolName, and SeriesDescription."""
	dicom_stats = defaultdict(int)

	for root, _, files in os.walk(folder_path):
		for file in files:
			file_path = os.path.join(root, file)
			try:
				dicom_data = pydicom.dcmread(file_path, stop_before_pixels=False)
				series_number = getattr(dicom_data, "SeriesNumber", "Unknown")
				protocol_name = getattr(dicom_data, "ProtocolName", "Unknown")
				series_description = getattr(dicom_data, "SeriesDescription", "Unknown")

				key = (series_number, protocol_name, series_description)
				dicom_stats[key] += 1
			except Exception as e:
				print(f"Skipping {file}: {e}")

	return dicom_stats

def write_log(log_file, dicom_stats):
	"""Writes the summary of DICOM counts to a log file."""
	with open(log_file, "w") as log:
		log.write("SeriesNumber, ProtocolName, SeriesDescription, Count\n")
		for (series, protocol, description), count in sorted(dicom_stats.items()):
			log.write(f"{series}, {protocol}, {description}, {count}\n")

def cleanup_folder(folder_path):
	"""Deletes the extracted folder after processing."""
	shutil.rmtree(folder_path, ignore_errors=True)



if __name__ == "__main__":

	raw_data_folder_list = glob.glob('D:/MatterNeurofeedback/raw_data/*/*/*/MATTER*.zip')


	print(f'Found {len(raw_data_folder_list)} folders.\n\n')

	for zip_path in raw_data_folder_list:

		log_file = f"{os.path.dirname(zip_path)}/dicom_log.txt"


		if not check_log_file(log_file):
			print(f'Working on folder: {zip_path}')
			extract_to = zip_path[:-4]

			unzip_folder(zip_path, extract_to)
			dicom_stats = process_dicom_files(extract_to)
			write_log(log_file, dicom_stats)
			cleanup_folder(extract_to)

			print(f"Log file '{log_file}' created successfully. Extracted folder deleted.\n")
