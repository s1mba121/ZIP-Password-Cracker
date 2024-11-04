# ZIP Password Cracker

This repository contains a **ZIP Password Cracker** tool that uses brute force and dictionary attacks to attempt to unlock password-protected ZIP, RAR, and 7z archives. With support for multi-threading, customizable character sets, and optional clustering, this tool is designed for efficiency and versatility.

## Features

- **Brute Force Attack**: Generates passwords based on specified parameters (length, character set).
- **Dictionary Attack**: Uses a list of passwords from a file.
- **Cluster Mode**: Distributes password attempts across multiple nodes.
- **Language Selection**: Interface messages are available in English and Russian.
- **Multi-format Support**: Works with `.zip`, `.rar`, and `.7z` archives.

## Requirements

- **Python 3.6+**
- Required Python packages:
  - `zipfile`
  - `rarfile`
  - `py7zr`
  - `argparse`
  - `tqdm` (for progress bar)
  - `concurrent.futures` (for threading)

To install necessary packages, run:
```bash
pip install rarfile py7zr tqdm
```

## Usage

The basic command to run the tool:
```bash
python zip_password_cracker.py <archive_file> [options]
```

### Command-Line Arguments

- `<archive_file>`: Path to the archive file you want to crack.
- `-n`, `--numeric`: Use only numeric characters for brute force.
- `-c`, `--cluster`: Activate cluster mode for distributed password attempts.
- `--total-nodes <int>`: Total nodes in cluster mode.
- `--node-index <int>`: Index of the current node (starting from 0).
- `-f`, `--password-file <path>`: Path to a dictionary file with potential passwords.
- `--lang <ru|en>`: Choose interface language (default is English).
- `-d`, `--debug`: Enable debug mode to display each attempted password.

### Examples

1. **Brute Force with Numeric Characters Only**
   ```bash
   python zip_password_cracker.py archive.zip -n
   ```

2. **Dictionary Attack Using a Password List**
   ```bash
   python zip_password_cracker.py archive.zip -f passwords.txt
   ```

3. **Clustered Brute Force Attack**
   ```bash
   python zip_password_cracker.py archive.zip -c --total-nodes 4 --node-index 1
   ```

### Output

The program will display real-time progress and will save the password to a file if the archive is unlocked successfully.

## Notes

- **Cluster Mode**: `--total-nodes` and `--node-index` are required in cluster mode.
- **Character Set**: For brute force without `-n`, it uses lowercase letters and digits.
- **Debug Mode**: Useful for tracking password attempts, especially in custom or debug testing.

## ASCII Art

The program displays ASCII art when it starts:
```
         _nnnn_                      
        dGGGGMMb
       @p~qp~~qMb
       M|@||@) M|
       @,----.JM|
      JS^\__/  qKL
     dZP        qKRb
    dZP          qKKb
   fZP            SMMb
   HZM  s1mba121  MMMM
   FqM            MMMM
 __| ".        |\dS"qML
 |    `.       | `' \Zq
_)      \.___.,|     .'
\____   )MMMMMM|   .'
     `-'       `--'

🔒 ZIP Password Cracker 🔒
```

## Disclaimer

This tool is for educational and legal use only. Do not use it on unauthorized files.

