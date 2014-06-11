# Backs up files from a source directory to a specified backup directory

import datetime
import os
import os.path
import shutil
import time


def main():

    print("-----------------------------------------")
    print("WELCOME TO BackItUp!")
    print("-----------------------------------------")
    print("Back it up. Back it in. Let me begin.")

    if not check_setup():
        create_config()

    source_directory, backup_directory, ignore_directories = read_config()

    confirm_backup = raw_input("Would you like to backup "
                               "your files now? [y/n]: ").lower()
    if not confirm_backup or confirm_backup not in "yes":
        quit()

    print("The files and following subdirectories within {} will be backed up:"
          .format(source_directory))

    valid_subdirs = [subdir for subdir in return_subdirectories_in_directory
                     (source_directory) if subdir not in ignore_directories]

    for subdir in valid_subdirs:
        print(subdir)
    confirm_source = raw_input("Please confirm this is correct [y/n]: ")
    if not confirm_source or confirm_source not in "yes":
        quit()

    print("The files will be copied to {}".format(backup_directory))
    confirm_destination = raw_input("Please confirm this is correct [y/n]: ")
    if not confirm_destination or confirm_destination not in "yes":
        quit()

    source_file_list = return_files_in_directory(source_directory,
                                                 ignore_directories)
    print("Elements in source_file_list: {}".format(len(source_file_list)))
    copied_files = batch_copy_files(source_directory, backup_directory,
                                    source_file_list)
    with open("log", "a") as f:
        f.write("Backup made on {}\n".format(datetime.datetime.now().
                                             strftime("%d/%m/%y at %H:%M")))
        f.write("{} files backed up\n\n".format(copied_files))
    print("Backup complete. {} files copied. Have a nice day."
          .format(copied_files))


def return_subdirectories_in_directory(source_directory="."):
    subdir_list = []
    for dirname, dirnames, filenames in os.walk(source_directory):
        if dirname == source_directory:
            for subdirname in dirnames:
                if "." not in subdirname and "Backup" not in subdirname:
                    subdir_list.append(os.path.join(dirname, subdirname))

    return subdir_list


def return_files_in_directory(source_directory=".", ignore_list=None):
    if ignore_list is None:
        ignore_list = []

    file_list = []
    print(ignore_list)
    for dirname, dirnames, filenames in os.walk(source_directory):

        skip = False
        for ignored_folder in ignore_list:
            if ignored_folder in dirname:
                skip = True

        if not skip:
            for filename in filenames:
                file_list.append(os.path.join(dirname, filename))
    return file_list


def check_setup():
    try:
        with open("./config") as f:
            return True
    except IOError:
        return False


def read_config():
    with open("./config") as f:
        f.readline()
        source_directory = f.readline().strip('\n')
        f.readline()
        backup_directory = f.readline().strip('\n')
        f.readline()
        ignore_directories = []
        for line in f:
            ignore_directories.append(line.strip('\n'))

    return (source_directory, backup_directory, ignore_directories)


def create_config():
    source_directory = get_directory("source directory")
    backup_directory = get_directory("backup directory")
    ignore_directory_list = get_ignore_list(source_directory)
    with open("./config", "w") as f:
        f.write("# Source directory:\n")
        f.write("{}\n".format(os.path.join(source_directory, '')))
        f.write("# Backup directory:\n")
        f.write("{}\n".format(os.path.join(backup_directory, 'Backup/')))
        f.write("# Ignored subdirectories:\n")
        for subdir in ignore_directory_list:
            f.write("{}\n".format(subdir))
    print("Configuration file created.")

    new_backup_location = os.path.join(backup_directory, "Backup/Current")
    new_archive_location = os.path.join(backup_directory, "Backup/Archive")

    if not os.path.exists(new_backup_location):
        os.makedirs(new_backup_location)
        print("New current backup folder created.")
    if not os.path.exists(new_archive_location):
        os.makedirs(new_archive_location)
        print("New archive backup folder created.")


def get_directory(directory_name):
    while True:
        directory_path = raw_input("\nPlease enter the destination of "
                                   "the {}.\n{}: "
                                   .format(directory_name,
                                           directory_name.title()))

        check_input = raw_input("\nYou entered: {}\n"
                                "Please confirm [y/n]: "
                                .format(directory_path)).lower()
        if check_input in "yes":
            if os.path.exists(directory_path):
                return directory_path
            else:
                print("That is not a valid directory.")


def get_ignore_list(directory):
    ignore_list = []
    exit = False
    subdirectory_in_directory = return_subdirectories_in_directory(directory)

    while not exit:
        print("Subdirectories in the source directory:")
        for n, subdirectory in enumerate(subdirectory_in_directory):
            print("{}. {}".format(n+1, subdirectory))
        print("Please enter the number for any subdirectories that should not "
              "be included in the backup process. "
              "Press <Enter> to save and exit.")
        ignore_directory = raw_input("Ignore number: ")
        if not ignore_directory:
            exit = True
        elif ignore_directory in str(range(1,
                                     len(subdirectory_in_directory)+1)):
            ignore_list.append(subdirectory_in_directory
                               [int(ignore_directory)-1])
            del(subdirectory_in_directory[int(ignore_directory)-1])
            print("Subdirectory added to ignore list.")
        else:
            print("That is not a valid subdirectory.")
    ignore_list.append(os.path.join(directory, "."))
    ignore_list.append(os.path.join(directory, "Backup/"))
    return ignore_list


def batch_copy_files(source_directory, destination_directory, files_to_copy):
    n = 0
    for source_file_path in files_to_copy:

        destination_file_path = "{}{}{}".format(
            destination_directory, "Current/",
            source_file_path[len(source_directory):])

        source_modified_date = int((datetime.datetime.fromtimestamp(os.path.
                                   getmtime(source_file_path))).
                                   strftime("%y%m%d%H%M"))
        try:
            destination_modified_date = int((datetime.datetime.fromtimestamp
                                            (os.path.getmtime
                                             (destination_file_path)))
                                            .strftime("%y%m%d%H%M"))
        except OSError:
            # Catches files which do not already exist in destination directory
            # Makes sure the destination directory
            # exists and create it if not so files can be copied
            destination_file_folder = os.path.split(destination_file_path)[0]
            if not os.path.exists(destination_file_folder):
                os.makedirs(destination_file_folder)
            copy_file(source_file_path, destination_file_path)
            n += 1
        else:
            # Only want to replace the file if the source file is newer
            if (source_modified_date > destination_modified_date):
                archive_file(source_directory, destination_directory,
                             source_file_path, destination_file_path,
                             source_modified_date)
                copy_file(source_file_path, destination_file_path)
                n += 1
    return n


def copy_file(source_path, destination_path):
    try:
        shutil.copy2(source_path, destination_path)
    except IOError:
        # Catches and ignores files with copy permissions
        pass


def archive_file(source_directory, destination_directory, source_file_path,
                 destination_file_path, source_modified_date):
    archive_path = "{}{}{}-{}".format(destination_directory, "Archive/",
                                      source_file_path[len(source_directory):],
                                      source_modified_date)
    shutil.move(destination_file_path, archive_path)


if __name__ == "__main__":
    main()