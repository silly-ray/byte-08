# 🖥️ BYTE 08 🖥️

## Overview 🖊️
This project automates the process of soslving the EE08 informatics exam

This tool uses the `EE08.sqlite` database to fetch the correct answers to given questions. It ***may not*** always score 100% on the exam because there are some questions in EE08's original database that cannot be found in the local `EE08.sqlite` database. However, the number of those questions is very low

**At this moment**, EE08 claims to have 2,265 questions in their database, while our database contains 2,253 questions

## Usage 🔨
```bash
# Clone the repository
git clone https://github.com/silly-ray/byte-08 "BYTE 08"

# Navigate to the project directory
cd "BYTE 08"

# Install the required dependencies
pip install -r requirements.txt

# Execute the script
python main.py
```