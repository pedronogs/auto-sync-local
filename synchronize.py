from __future__ import print_function
import pickle
import json
import os
import io
import sys
import shutil

CONFIGS = None

class LocalFolder(object):
    def __init__(self, local_folder_path, network_folder_path):
        self.local_path = local_folder_path
        self.network_path = network_folder_path

    # Get file timestamp
    def get_file_timestamp(cls, file_path):
        return int(os.path.getmtime(file_path))


    # List files on local or network folders
    def list_files(self, folder_path):
        return os.listdir(folder_path)  


    # 'Download' (Network -> Local) or 'Upload' (Local -> Network) file between network and local folders
    def copy_file(self, source_path, dest_path, download = True, update = False):
        # Get filename from path
        filename = source_path.rsplit('/', 1)[-1]

        # Copy file between folders
        try: 
            shutil.copyfile(source_path, dest_path)

            file_timestamp = self.get_file_timestamp(source_path)
            os.utime(dest_path, (file_timestamp, file_timestamp)) # Change modification time to match both files
        except:
            print("Error copying '{}' from {} to {}.".format(filename, source_path, dest_path))
            return False
        
        # Print result
        if update == True:
            print("\nFile '{}' updated successfully in folder '{}'.".format(filename, dest_path))
        elif download == True:
            print("\nFile '{}' downloaded successfully in folder '{}'.".format(filename, dest_path))
        else:
            print("\nFile '{}' uploaded successfully in folder '{}'.".format(filename, dest_path))

        return True


    # Recursive method to synchronize all folder and files between both folders
    def synchronize(self, local_folder_path = None, network_folder_path = None):
        # print("------------- Synchronizing folder '{}' -------------".format(local_path.rsplit('\\', 1)[-1]), end="\r")
        
        # First iteration (set path as root folders)
        if local_folder_path == None:
            local_folder_path = self.local_path

        if network_folder_path == None:
            network_folder_path = self.network_path

        # Check if folder paths exists, if not, creates folder
        if not os.path.exists(local_folder_path):
            os.makedirs(local_folder_path)

        if not os.path.exists(network_folder_path):
            os.makedirs(network_folder_path)

        # List local and network files
        local_files = self.list_files(local_folder_path)
        network_files = self.list_files(network_folder_path)

        # Compare files (and folders, recursively) with same name in both origins
        # If any file is newer, update
        same_files = list(set(local_files) & set(network_files))
        for sm_file in same_files:
            local_absolute_path = "{}/{}".format(local_folder_path, sm_file)
            network_absolute_path = "{}/{}".format(network_folder_path, sm_file)

            # Checks if files were modified on any origin
            local_file_mtime = self.get_file_timestamp(local_absolute_path)
            network_file_mtime = self.get_file_timestamp(network_absolute_path)

            # Modification in local file
            if local_file_mtime > network_file_mtime:
                if os.path.isdir(local_absolute_path):
                    self.synchronize(local_absolute_path, network_absolute_path) # Recursively synchronize files inside another folder
                else:
                    self.copy_file(local_absolute_path, network_absolute_path, False, True) # Upload
    
            # Modification in network file
            elif local_file_mtime < network_file_mtime:
                if os.path.isdir(network_absolute_path):
                    self.synchronize(local_absolute_path, network_absolute_path) # Recursively synchronize files inside another folder
                else:
                    self.copy_file(network_absolute_path, local_absolute_path, True, True) # Download

        # Compare different files in both origins and download/upload what is needed
        different_files = list(set(local_files) ^ set(network_files))
        for diff_file in different_files:
            local_absolute_path = "{}/{}".format(local_folder_path, diff_file)
            network_absolute_path = "{}/{}".format(network_folder_path, diff_file)

            # Download if file is only on network
            if diff_file in network_files:
                if os.path.isdir(network_absolute_path):
                    self.synchronize(local_absolute_path, network_absolute_path) # Recursively synchronize files inside another folder
                else:
                    self.copy_file(network_absolute_path, local_absolute_path, True) # Download

            # Upload if file is only local
            else:
                if os.path.isdir(local_absolute_path):
                    self.synchronize(local_absolute_path, network_absolute_path) # Recursively synchronize files inside another folder
                else:
                    self.copy_file(local_absolute_path, network_absolute_path, False) # Upload


def main():
    # Load configs file
    try:
        global CONFIGS
        CONFIGS = json.load(open("configs.json", "r", encoding='utf-8'))
    except:
        print("Please rename example file 'configs-example.json' to 'configs.json' and update all fields.")
        return

    # Instantiate LocalFolder class and synchronize files between local and network folders
    local_folder = LocalFolder(CONFIGS['local_folder_path'], CONFIGS['network_folder_path'])
    local_folder.synchronize()


if __name__ == '__main__':
    main()