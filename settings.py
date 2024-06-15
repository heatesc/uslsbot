import yaml
import sys
import os
import subprocess

CONFIG_DIR = "config_files"
BOT_PATH = "bot.py"


def load_config(config_filename):
    """
    Load the YAML configuration file.
    
    :param config_filename: Name of the configuration file
    :return: Configuration object
    """
    config_path = os.path.join(CONFIG_DIR, config_filename)
    try:
        with open(config_path, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except IOError as e:
        print(f"Invalid filename: '{config_filename}'")
        sys.exit(1)


def set_environment_variables(conf_obj) -> bool:
    """
    Set environment variables based on the configuration object.
    
    :param conf_obj: Configuration object
    """
    token_path = conf_obj.get('token_path')
    projects_info_channel_id = conf_obj.get('projects_info_channel_id')
    projects_info_message_id = conf_obj.get('projects_info_message_id')
    owner_user_id = conf_obj.get('owner_user_id')
    
    if not token_path:
        print("Token path not found in the configuration file.")
        return False

    try:
        with open(token_path, "r") as token_file:
            os.environ['DISCORD_TOKEN'] = token_file.read().strip()
        print("Discord token has been set successfully.")
    except IOError as e:
        print(f"Failed to read token from path: '{token_path}'")
        return False
        
    if projects_info_channel_id:
        os.environ['PROJECTS_INFO_CHANNEL_ID'] = projects_info_channel_id
        print("Projects info channel ID has been set successfully.")
    else:
        print("Projects info channel ID not found in the configuration file.")
        return False
    
    if projects_info_message_id:
        os.environ['PROJECTS_INFO_MESSAGE_ID'] = projects_info_message_id
        print("Projects info message ID has been set successfully.")
    else:
        print("Projects info message ID not found in the configuration file.")
        return False
    
    if owner_user_id:
        os.environ['OWNER_USER_ID'] = owner_user_id
        print("Owner user ID has been set successfully.")
    else:
        print("Owner user ID not found in the configuration file.")
        return False
    
    return True
    

def execute_script(script_path):
    """
    Execute a Python script from the given file path using subprocess.
    
    :param script_path: Path to the Python script
    """
    result = subprocess.run([sys.executable, script_path], check=True)
    if result.returncode != 0:
        print(f"Script {script_path} exited with code {result.returncode}")
        sys.exit(result.returncode)


def main():
    if len(sys.argv) != 2:
        print("Expected config filename.")
        return

    config_filename = sys.argv[1]
    conf_obj = load_config(config_filename)
    if not set_environment_variables(conf_obj):
        return
    execute_script(BOT_PATH)

if __name__ == "__main__":
    main()
