from msilib.schema import Directory
import sys
import os
from getpass import getpass
from platform import node
import shutil
import winreg
import subprocess
import yaml
import json
import time
import requests
from requests.exceptions import HTTPError
from tabulate import tabulate
from traceback import format_exc
from requests.packages.urllib3.exceptions import InsecureRequestWarning
################################################################################

os.system('cls')

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

## GETS CONFIGURATION SETTINGS FOR config.yaml #################################
################################################################################


def get_config_settings():
    os.system('cls')

    cml_username = ""
    while len(cml_username) == 0:
        cml_username = input("CML Username: ").strip()

    cml_password = ""
    while len(cml_password) == 0:
        cml_password_conf = ""
        cml_password = getpass("CML Password: ").strip()
        if len(cml_password) != 0:
            cml_password_conf = getpass("Confirm Password: ").strip()
            if cml_password == cml_password_conf:
                break
            else:
                cml_password = ""
                input("Passwords did not match\nPress Enter to try again...")

    cml_name_or_ip = ""
    while len(cml_name_or_ip) == 0:
        cml_name_or_ip = input("CML Name or IP Address: ").strip()

    config_settings = dict()
    config_settings['cml_user'] = cml_username
    config_settings['cml_pass'] = cml_password
    config_settings['cml_server'] = cml_name_or_ip

    return config_settings
################################################################################


## VALIDATES CONFIGURATION SETTINGS & GET BEARER TOKEN #########################
################################################################################

def validate_settings_get_token(cml_user, cml_pass, cml_server):
    print()

    # Base URL for future API calls
    base_url = "https://" + cml_server + "/api/v0"

    # Token required to authenticate API calls
    api_url_authenticate = base_url + "/authenticate"

    payload = json.dumps({
        "username": cml_user,
        "password": cml_pass
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    try:
        authenticate_response = requests.request(
            "POST", api_url_authenticate, headers=headers, data=payload, verify=False, timeout=3)
        authenticate_response.raise_for_status()
        authenticate_status_code = str(authenticate_response.status_code)
        token_text = authenticate_response.text
        token = token_text.strip('\"')
        if "200" in authenticate_status_code:
            print("AUTHENTICATION SUCCEEDED\n")

            validate_return = dict()
            validate_return['status_code'] = authenticate_status_code
            validate_return['cml_url'] = base_url
            validate_return['bearer_token'] = token

            return validate_return

    except requests.exceptions.ConnectTimeout as err:
        err = str(err)
        return err
    except requests.exceptions.HTTPError as err:
        err = str(err).split()
        return(err[0])
    except requests.exceptions.ConnectionError as err:
        err = str(err).split()
        return(err)
    except requests.exceptions.RequestException as err:
        err = str(err).split()
        return(err)
################################################################################


## LAB INFO ####################################################################
################################################################################

def get_lab_info(base_url, bearer_token):

    # Get lab info: lab title, lab state, and lab ID

    api_url_pop_lab_tiles = base_url + "/populate_lab_tiles"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + bearer_token
    }

    pop_lab_tiles_response = requests.request(
        "GET", api_url_pop_lab_tiles, headers=headers, data=payload, verify=False)

    pop_lab_tiles_response_json = pop_lab_tiles_response.json()
    lab_tiles = pop_lab_tiles_response_json['lab_tiles']
    lab_tiles_keys = list(lab_tiles.keys())

    labs = []
    lab_num = 0

    for lab_tile in lab_tiles_keys:
        lab_num += 1
        lab_titles = lab_tiles[lab_tile]['lab_title']
        lab_states = lab_tiles[lab_tile]['state']
        lab_ids = lab_tiles[lab_tile]['id']
        lab = [lab_num, lab_titles, lab_states, lab_ids]
        labs.append(lab)

    num_of_labs = len(labs) + 1

    lab_info = dict()
    lab_info['lab_details'] = labs
    lab_info['total_labs'] = num_of_labs
    lab_info['lab_tiles'] = lab_tiles

    return lab_info
################################################################################


## SELECT LAB ##################################################################
################################################################################

def lab_selector(labs):
    print(tabulate(labs, headers=["NUMBER", "LAB", "STATE", "UUID"]))
    print("\n" * 5)
    print("\n('q' to quit.)\n\n")

    while True:
        # print("\n('q' to quit.)\n\n")
        user_specified_lab = input(
            "Enter lab NUMBER you wish to generate sessions for from the list above: ")
        print()

        if "q" in user_specified_lab:
            print("Exiting")
            sys.exit(1)

        if user_specified_lab.isdigit():
            user_specified_lab = int(user_specified_lab)
            if user_specified_lab in range(1, num_of_labs):
                user_specified_lab = user_specified_lab - 1
                break
        else:
            user_specified_lab = user_specified_lab.lower()
            if "q" in user_specified_lab:
                print("Exiting")
                sys.exit(1)

    user_specified_lab = labs[user_specified_lab][3]

    return user_specified_lab
################################################################################


## SECURECRT PATH ##############################################################
################################################################################

def application_installed():
    # SecureCRT may or may not be in system PATH
    # This is how to find it whether it is or not
    program_files_32bit = os.environ.get('PROGRAMW6432')
    program_files_64bit = os.environ.get('PROGRAMFILES')
    securecrt_path_32bit = program_files_32bit + "\\VanDyke Software\\SecureCRT\\"
    securecrt_path_64bit = program_files_64bit + "\\VanDyke Software\\SecureCRT\\"
    securecrt_file = "SecureCRT.exe"
    securecrt_exists_32bit = os.path.exists(
        securecrt_path_32bit+securecrt_file)
    securecrt_exists_64bit = os.path.exists(
        securecrt_path_64bit+securecrt_file)

    if securecrt_exists_32bit:
        securecrt_path = securecrt_path_32bit
    elif securecrt_exists_64bit:
        securecrt_path = securecrt_path_64bit
    else:
        print(f"{securecrt_file} was not found.")
        print("Exiting")
        sys.exit(1)

    return securecrt_path, securecrt_file
################################################################################


## SECURECRT CONFIG PATH #######################################################
################################################################################

def config_path():
    application_installed()
    # Searching Windows registry
    # If exists, securecrt_dir will be set to seccrt_key[0]
    path = winreg.HKEY_CURRENT_USER
    seccrt_location = winreg.OpenKeyEx(path, r"SOFTWARE\\VanDyke\\SecureCRT\\")
    seccrt_key = winreg.QueryValueEx(seccrt_location, "Config Path")

    if seccrt_location:
        winreg.CloseKey(seccrt_location)
        seccrt_key = list(seccrt_key).pop(0)
        return seccrt_key
    else:
        print("SecureCRT configuration path was not found.")
        print("Exiting")
        sys.exit(1)
################################################################################


## VERIFY INITIAL CONFIG FILE EXISTS ###########################################
################################################################################

def initial_config_check():
    init_config_file = "initial_config"
    init_config_exists = os.path.exists(init_config_file)

    if init_config_exists:
        pass
    else:
        print(f"{init_config_file} was not found.")
        print("Exiting")
        sys.exit(1)
################################################################################


## VERIFY CML CONSOLE SERVER SESSION TEMPLATE FILE EXISTS ######################
################################################################################

def cml_console_server_check():
    init_console_server_session_file = "cml_console_server"
    init_console_server_session_file_exists = os.path.exists(
        init_console_server_session_file)

    if init_console_server_session_file_exists:
        pass
    else:
        print(f"{init_console_server_session_file} was not found.")
        print("Exiting")
        sys.exit(1)
################################################################################


## VERIFY CML CONSOLE SERVER SESSION TEMPLATE FILE EXIST #######################
################################################################################

def config_yaml_check():
    config_yaml_exists = os.path.exists(config_yaml)

    if config_yaml_exists:
        return True
    else:
        print(f"{config_yaml} was not found. \n\nBeginning Setup\n")
        return False
################################################################################


## SET CONFIG VARIABLES ########################################################
################################################################################

def set_config_variables():
    # Read config.yaml and assign field values to variables
    with open('config.yaml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        config = list(data.keys())
        cml_user_index = config.index('username')
        cml_pass_index = config.index('password')
        cml_server_index = config.index('controller')
        cml_user = data[config[cml_user_index]]
        cml_pass = data[config[cml_pass_index]]
        cml_server = data[config[cml_server_index]]

        cml_configs = dict()
        cml_configs['cml_user'] = cml_user
        cml_configs['cml_pass'] = cml_pass
        cml_configs['cml_server'] = cml_server

        return cml_configs
################################################################################


## CREATE DIRECTORY FOR LAB SESSIONS ###########################################
################################################################################

def create_lab_session_dir():
    node_session_dir = os.path.join(
        sessions_cml_labs_dir, lab_title)
    try:
        os.makedirs(node_session_dir, exist_ok=True)
        print(f"Directory for lab '{lab_title}' created successfully")
        print("=" * 79)
        return node_session_dir
    except OSError as error:
        print(f"Directory for lab '{lab_title}' can not be created")
        print("Exiting")
        sys.exit(1)
################################################################################


## GENERATE NODE SESSIONS ######################################################
################################################################################

def generate_node_sessions_files(node_session_dir):
    print()
    print("Generating session files.")
    print("=" * 79)

    node_session_template_filename = 'node_session_template'
    node_session_template_location = sessions_cml_labs_dir + \
        '\\' + node_session_template_filename

    # List of nodes that do not need sessions created because they do not have console access
    ignore_node_definitions = ["external_connector", "unmanaged_switch"]

    search_cml_node_cmd_lab_title = "CHANGEME_LAB_TITLE"
    search_cml_node_cmd_label = "CHANGEME_NODE_LABEL"

    for lab_node in lab_nodes:
        lab_node_definition = lab_node['node_definition']
        if lab_node_definition not in ignore_node_definitions:
            lab_node_label = lab_node['label']
            lab_node_label_command = lab_node_label
            for invalid_char in invalid_chars:
                if invalid_char in lab_node_label:
                    new_lab_node_label = lab_node_label.replace(
                        invalid_char, "_").strip()
                    lab_node_label = new_lab_node_label

            node_session_filename = lab_node_label + '.ini'
            node_session_location = node_session_dir + '\\' + node_session_filename
            node_session_file = shutil.copyfile(
                node_session_template_location, node_session_location)

            with open(node_session_file, 'r') as f:
                node_session_data = f.read()
                node_session_data = node_session_data.replace(
                    search_cml_node_cmd_lab_title, lab_title_command)
                node_session_data = node_session_data.replace(
                    search_cml_node_cmd_label, lab_node_label_command)

            with open(node_session_file, 'w') as f:
                f.write(node_session_data)

    print()
    print(f"Generation of node session files for lab '{lab_title}' complete")
    print("Exiting")
    print("=" * 79)
################################################################################


## SETUP #######################################################################
################################################################################

def setup():
    search_username = "CHANGEME_USER"
    search_contr = "CHANGEME_CONTR"
    search_cml_cmd = "CHANGEME_CMD"
    replace_cml_contr_cmd = "quit"

    console_session_template_filename = init_console_server_session_file + '.ini'
    console_session_template_location = sessions_dir + \
        '\\' + console_session_template_filename

    node_session_template_filename = 'node_session_template'
    node_session_template_location = sessions_dir + \
        '\\' + node_session_template_filename

    print(f"{config_yaml} was not found.\nStarting Setup\n")
    while True:
        config_settings = get_config_settings()
        os.system('cls')
        print(
            f"\nVALIDATING ACCOUNT {config_settings['cml_user']} AGAINST {config_settings['cml_server']}\n")
        validate_return = validate_settings_get_token(
            config_settings['cml_user'], config_settings['cml_pass'], config_settings['cml_server'])
        if validate_return:
            message1 = (f"Try entering configuration settings again.\n"
                        f"Press Enter to continue...")
            if "403" in validate_return:
                while "403" in validate_return:
                    print("AUTHENTICATION FAILED\n")
                    input(message1)
                    break
            elif "timeout" in validate_return:
                while "timeout" in validate_return:
                    print(
                        f"ERROR:   COULD NOT CONTACT {config_settings['cml_server']} \nREASON:  TIMEOUT\n")
                    input(message1)
                    break
            elif "getaddrinfo" in validate_return:
                while "getaddrinfo" in validate_return:
                    print(
                        f"ERROR:   BAD HOSTNAME OR ADDRESS: {config_settings['cml_server']}\n")
                    input(message1)
                    break
            elif "200" in validate_return['status_code']:
                bearer_token = validate_return['bearer_token']
                base_url = validate_return['cml_url']
                break
            else:
                print("Something went wrong\n")
                print(validate_return)
                input(message1)
        else:
            print("Something went wrong\n")
            print(validate_return)
            input(message1)

    def create_config_yaml():
        print("Creating config.yaml file.")

        search_cml_username = "CHANGEME_USER"
        search_cml_password = "CHANGEME_PASS"
        search_cml_name_or_ip = "CHANGEME_CML"

        with open(r'initial_config', 'r') as f:
            data = f.read()
            data = data.replace(search_cml_username,
                                config_settings['cml_user'])
            data = data.replace(search_cml_password,
                                config_settings['cml_pass'])
            data = data.replace(search_cml_name_or_ip,
                                config_settings['cml_server'])

        with open(r'config.yaml', 'w') as f:
            f.write(data)

        print()
        # print("Creating cml_console_server.ini session file.")

    def create_console_server_session_file(cml_user, cml_server):
        # Creating cml_console_server session file
        console_session_template_file = shutil.copyfile(
            init_console_server_session_file, console_session_template_location)

        # Replacing placeholder USERNAME and HOSTNAME values with those found in config.yaml
        with open(console_session_template_file, 'r') as f:
            console_session_data = f.read()
            console_session_data = console_session_data.replace(
                search_username, cml_user)
            console_session_data = console_session_data.replace(
                search_contr, cml_server)
            console_session_data = console_session_data.replace(
                search_cml_cmd, replace_cml_contr_cmd)

        with open(console_session_template_file, 'w') as f:
            f.write(console_session_data)

        def get_encrypted_seccrt_creds():
            print()
            print("Creating cml_console_server.ini session file.")

            seccrt = securecrt_path + securecrt_file
            print("Launching SecureCRT with cml_console_server session")
            cmd = [seccrt, '/T', '/S', 'cml_console_server']
            print()
            print()
            print("Close SecureCRT once the cml_console_server session disconnects\n\n")

            try:
                subprocess.run(cmd, timeout=10, check=True
                               )
            except FileNotFoundError as exc:
                print(
                    f"Process failed because the executable could not be found.\n{exc}")
                print("\nExiting")
                sys.exit(1)
            except subprocess.CalledProcessError as exc:
                print(
                    f"Process failed because did not return a successful return code. "
                    f"Returned {exc.returncode}\n{exc}"
                )
                print("\nExiting")
                sys.exit(1)
            except subprocess.TimeoutExpired as exc:
                print(f"Process timed out.\n{exc}")
                print("\nExiting")
                sys.exit(1)

            os.system('cls')

            print()
            print("Console server session template file created")
            print("=" * 79)

        get_encrypted_seccrt_creds()

    def create_cml_sessions_dir():
        cml_server_dir = 'CML ' + cml_server + ' Labs'
        sessions_cml_labs_dir = os.path.join(
            sessions_dir, cml_server_dir)
        try:
            os.makedirs(sessions_cml_labs_dir, exist_ok=True)
            print(f"Directory '{cml_server_dir}' created successfully")
            print("=" * 79)
            return sessions_cml_labs_dir
        except OSError as error:
            print(f"Directory '{cml_server_dir}' could not be created")
            print("Exiting")
            sys.exit(1)

    def create_node_session_template_file():
        console_session_template_file = console_session_template_location
        replace_cml_node_cmd = "open /CHANGEME_LAB_TITLE/CHANGEME_NODE_LABEL/0"

        sessions_cml_labs_dir = create_cml_sessions_dir()
        node_session_template_location = sessions_cml_labs_dir + \
            '\\' + node_session_template_filename

        # Creating node session template file
        node_session_template_file = shutil.copyfile(
            console_session_template_file, node_session_template_location)

        # Replacing placeholder USERNAME and HOStNAME values with those found in config.yaml
        search_cml_contr_cmd = replace_cml_contr_cmd

        with open(node_session_template_file, 'r') as f:
            node_session_data = f.read()
            node_session_data = node_session_data.replace(
                search_cml_contr_cmd, replace_cml_node_cmd)

        with open(node_session_template_file, 'w') as f:
            f.write(node_session_data)

    def housekeeping():
        # Deleting cml_console_server.ini template file
        print()
        if os.path.exists(console_session_template_location):
            print(f"Deleting {console_session_template_location}")
            os.remove(console_session_template_location)
        else:
            print(f"{console_session_template_location} does not exist")
            print("Exiting")
            sys.exit(1)

        print("=" * 79)

        print()
        print("Node session template file generation complete")
        print("=" * 79)

    create_config_yaml()

    cml_configs = set_config_variables()
    cml_user = cml_configs['cml_user']
    cml_server = cml_configs['cml_server']

    time.sleep(1)

    create_console_server_session_file(cml_user, cml_server)

    create_node_session_template_file()

    housekeeping()

################################################################################


running = True
while running:
    securecrt = application_installed()
    securecrt_path = securecrt[0]
    securecrt_file = securecrt[1]

    config_dir = config_path()
    sessions_dir = config_dir + '\Sessions'

    initial_config_check()
    init_console_server_session_file = "cml_console_server"

    cml_console_server_check()

    config_yaml = "config.yaml"

    while True:
        config_yaml_exists = config_yaml_check()

        if config_yaml_exists:
            cml_configs = set_config_variables()
            cml_user = cml_configs['cml_user']
            cml_pass = cml_configs['cml_pass']
            cml_server = cml_configs['cml_server']

            sessions_cml_labs_dir = sessions_dir + \
                '\CML ' + cml_server + ' Labs'
            sessions_cml_labs_dir_exists = os.path.exists(
                sessions_cml_labs_dir)

            if sessions_cml_labs_dir_exists is False:
                input(
                    f"The directory {sessions_cml_labs_dir} was not found.\nPress Enter to begin setup...")
                os.remove(config_yaml)
                break

            print(
                f"\nVALIDATING ACCOUNT {cml_user} AGAINST {cml_server}\n")

            validate_return = validate_settings_get_token(
                cml_user, cml_pass, cml_server)

            if isinstance(validate_return, dict):
                base_url = validate_return['cml_url']
                token = validate_return['bearer_token']
            else:
                input("AUTHENTICATION FAILED\nPress Enter to begin setup...\n")
                os.remove(config_yaml)
                break

            lab_info = get_lab_info(
                base_url, token)
            labs = lab_info['lab_details']
            num_of_labs = lab_info['total_labs']

            lab_selection = lab_selector(labs)

            invalid_chars = ("<", ">", ":", "\"", "\/", "\\", "|", "?", "*")

            lab_nodes = lab_info['lab_tiles'][lab_selection]['topology']['nodes']
            lab_title = lab_info['lab_tiles'][lab_selection]['lab_title']
            lab_title_command = lab_title

            for invalid_char in invalid_chars:
                if invalid_char in lab_title:
                    lab_title_command = lab_title
                    new_lab_title = lab_title.replace(
                        invalid_char, "_").strip()
                    lab_title = new_lab_title

            node_session_dir = create_lab_session_dir()

            generate_node_sessions_files(node_session_dir)

            running = False
            break
        else:
            setup()
            os.system('cls')
            break
