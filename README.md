# SecureCRT Session Generator for Cisco Modeling Labs (CML) 


[![Python3.10](https://img.shields.io/static/v1?label=Python&logo=Python&color=3776AB&message=3.10)](https://www.python.org/)
![Windows]( 	https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![macOS](https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=apple&logoColor=white)



## Introduction

The purpose of this project is to make console access to devices in CML more convenient by allowing users to automate the creation of SecureCRT session files. It leverages CML's built-in `console server` (not the Breakout Tool).

Each session file will be named to match its associated device/node name in the lab and will display that name in the tab in SecureCRT when the session is used.

## Demo
![Demo](./docs/images/demo.gif)

## Screenshots
![Screenshot](./docs/images/lab_selection.png)
![Screenshot](./docs/images/seccrt_and_cml.png)
![Screenshot](./docs/images/seccrt_consoled_in.png)

## Requirements

- Windows 10 (possibly 11) or macOS 12 (possibly 13)
- Python 3
- SecureCRT 8.7.2 or later
- CML 2.2.2 or later

## Downloading From GitHub
### Git Clone Method (requires Git)
- If Git is installed on your system, continue
- Click the `Code` button at the top of the page
- Copy the link
- Open PowerShell/Command Prompt if Windows or Terminal if macOS
- Navigate to the directory you would like to download this project to
- Enter the following command:

        git clone https://github.com/bruceLstanton/securecrt-session-generator-for-cml.git
- The project should have downloaded to a directory with the name of this project
- That directory will be the `source directory` referenced in the `Installation` and `Usage` sections below

### ZIP Download Method
- Click the `Code` button at the top of the page
- Click `Download ZIP`
- Extract the ZIP/archive to your desired directory location
- That directory will be the `source directory` referenced in the `Installation` and `Usage` sections below

## Installation - Windows
- Internet connectivity required
- Recommend using **venv**
- The source directory can be placed anywhere. It can be renamed if desired

### Scripted Method
- Execute **install.bat** from within the source directory
- **install.bat** will instantiate a virtual environment within the source directory and download/install all necessary Python packages within the environment

### Manual Method
- Open a terminal
- Navigate to the source directory
- Execute the following command to create the virtual environment:

        python -m venv venv

- Activate the virtual environment:

        ./venv/Scripts/activate

- Install the necessary Python packages for the virtual environment:

        pip3 install -r requirements.txt

- Deactivate the virtual environment:

        deactivate

## Installation - macOS
- Internet connectivity required
- Recommend using **venv**
- The source directory can be placed anywhere. It can be renamed if desired

### Manual Method
- Open a terminal
- Navigate to the source directory
- Execute the following command to create the virtual environment:

        python3 -m venv venv

- Activate the virtual environment:

        source venv/bin/activate

- Install the necessary Python packages for the virtual environment:

        pip3 install -r requirements.txt

- Deactivate the virtual environment:

        deactivate

- Make the **session_gen.py** script executable:

        chmod +x session_gen.py
## Usage - Windows

### Scripted Method
- Execute the **crt_session_generator.bat** from the source directory or via a shortcut to it
- Follow the prompts in the terminal

### Manual Method
- Open a command prompt/PowerShell session
- Navigate to the source directory. Execute the following command:

        .\venv\Scripts\python.exe session_gen.py

- Follow the prompts in the terminal
## Usage - macOS

### Manual Method
- Open a terminal
- Navigate to the source directory. Execute the following command:

        ./venv/bin/python3 session_gen.py

- Follow the prompts in the terminal

### Notes & Disclaimers
- Neither I nor this project is associated with Cisco Systems, Inc. or VanDyke Software in any way.
- **I am not a "mac guy".** Cross-compatibility development was done on a macOS Monterey VM.
- Credentials and CML IP/hostname are stored in **cleartext** in config.yaml. This was orignally meant to mimic how the Breakout Tool operates.
- Deleting **config.yaml** will allow the user to re-enter CML credentials and host information the next time the script is executed.
- The password stored in the session files are encrypted by SecureCRT if setup was follwed as instructed.
- This tool only needs to be run to generate sessions for existing labs, new labs, changes (additions, removals, renamings) to devices in existing labs for which sessions have already been created, or if a lab has been renamed that has had sessions generated.
- This tool does not need to be running in order for console sessions to function.
