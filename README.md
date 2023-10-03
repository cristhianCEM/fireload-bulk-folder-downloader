# Auto Downloader for Fireload Folders
This Python script enables automatic downloading of files from Fireload folders using Selenium for web interaction and Multiprocessing for concurrent downloads.

## Installation
First, ensure you have Python installed on your machine. This script has been tested with Python 3.8, but other versions may work as well.

Install the required libraries using pip:
```bash
pip install -r requirements.txt
```

## Usage
Update the config.py file with the URL of the Fireload folder you wish to download files from.

Run the script:
```bash
python main.py -p <number of processes> -url <Fireload folder URL>
```

This will start the Selenium browser, navigate to the specified Fireload folder, gather the download links, and download the files concurrently using multiple processes.

## Contributing
Feel free to fork this repository and submit pull requests for any improvements or additional features you may implement.