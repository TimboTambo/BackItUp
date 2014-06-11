# Backs up files from a source dir to a specified backup dir

import datetime
import os
import os.path
import shutil
import time


def main():

    print_welcome()
    if not already_setup():
        create_config()
    source_dir, backup_dir, ignore_dirs = read_config()
    if confirm_backup_details(source_dir, backup_dir, ignore_dirs):
        source_file_list = return_files_in_dir(source_dir, ignore_dirs)
        num_copied_files = batch_copy_files(source_dir, backup_dir,
                                            source_file_list)
        update_log(num_copied_files)
        print("Backup complete. {} files copied. Have a nice day."
              .format(num_copied_files))


def print_welcome():
    print("-----------------------------------------")
    print("WELCOME TO BackItUp!")
    print("-----------------------------------------")
    print("Back it up. Back it in. Let me begin.")


def already_setup():
    try:
        with open("./config") as f:
            return True
    except IOError:
        return False


def create_config():
    source_dir = get_dir("source directory")
    backup_dir = get_dir("backup directory")
    ignore_dir_list = get_ignore_list(source_dir)
    with open("./config", "w") as f:
        f.write("# Source directory:\n")
        f.write("{}\n".format(os.path.join(source_dir, '')))
        f.write("# Backup directory:\n")
        f.write("{}\n".format(os.path.join(backup_dir, 'Backup/')))
        f.write("# Ignored subdirs:\n")
        for subdir in ignore_dir_list:
            f.write("{}\n".format(subdir))
    print("Configuration file created.")

    new_backup_location = os.path.join(backup_dir, "Backup/Current")
    new_archive_location = os.path.join(backup_dir, "Backup/Archive")

    if not os.path.exists(new_backup_location):
        os.makedirs(new_backup_location)
        print("New 'Current' backup folder created.")
    if not os.path.exists(new_archive_location):
        os.makedirs(new_archive_location)
        print("New 'Archive' backup folder created.")


def get_dir(dir_name):
    while True:
        dir_path = raw_input("\nPlease enter the destination of the {}.\n{}: "
                             .format(dir_name, dir_name.title()))

        check_input = raw_input("\nYou entered: {}\n"
                                "Is this correct? [y/n]: "
                                .format(dir_path)).lower()
        if check_input in "yes":
            if os.path.exists(dir_path):
                return dir_path
            elif os.path.exists("/{}".format(dir_path)):
                return os.path.join("/", dir_path)
            else:
                print("That is not a valid directory.")


def get_ignore_list(source_dir):
    ignore_list = []
    user_exit = False
    subdir_in_dir = return_subdirs_in_dir(source_dir)

    while not user_exit and len(subdir_in_dir) > 0:
        print("Subdirectories in the source directory:")
        for n, subdir in enumerate(subdir_in_dir):
            print("{}. {}".format(n+1, subdir))
        print("Please enter the number for any subdirectories that should not "
              "be included in the backup process."
              "Press <Enter> to save and exit.")
        ignore_dir = raw_input("Ignore number: ")
        if not ignore_dir:
            exit = True
        elif ignore_dir in str(range(1, len(subdir_in_dir)+1)):
            ignore_list.append(subdir_in_dir[int(ignore_dir)-1])
            del(subdir_in_dir[int(ignore_dir)-1])
            print("Subdirectory added to ignore list.")
        else:
            print("That is not a valid subdirectory.")
    ignore_list.append(os.path.join(source_dir, "."))
    ignore_list.append(os.path.join(source_dir, "Backup/"))
    return ignore_list


def read_config():
    with open("./config") as f:
        f.readline()
        source_dir = f.readline().strip('\n')
        f.readline()
        backup_dir = f.readline().strip('\n')
        f.readline()
        ignore_dirs = [line.strip('\n') for line in f]

    return (source_dir, backup_dir, ignore_dirs)


def confirm_backup_details(source_dir, backup_dir, ignore_dirs):
    confirm_backup = raw_input("Would you like to backup "
                               "your files now? [y/n]: ").lower()
    if not confirm_backup or confirm_backup not in "yes":
        quit()

    print("The files and following subdirectories within {} will be backed up:"
          .format(source_dir))

    valid_subdirs = [subdir for subdir in return_subdirs_in_dir(source_dir)
                     if subdir not in ignore_dirs]
    for subdir in valid_subdirs:
        print(subdir)

    confirm_source = raw_input("Please confirm this is correct [y/n]: ")
    if not confirm_source or confirm_source not in "yes":
        print("Please edit or delete the config file and try again.")
        quit()

    print("The files will be copied to {}".format(backup_dir))
    confirm_destination = raw_input("Please confirm this is correct [y/n]: ")
    if not confirm_destination or confirm_destination not in "yes":
        print("Please edit or delete the config file and try again.")
        quit()

    return True


def return_subdirs_in_dir(source_dir="."):
    subdir_list = []
    for dirname, dirnames, filenames in os.walk(source_dir):
        if dirname == source_dir:
            for subdirname in dirnames:
                if "." not in subdirname and "Backup" not in subdirname:
                    subdir_list.append(os.path.join(dirname, subdirname))

    return subdir_list


def return_files_in_dir(source_dir=".", ignore_list=None):
    if ignore_list is None:
        ignore_list = []

    file_list = []

    for dirname, dirnames, filenames in os.walk(source_dir):
        skip = False
        for ignored_folder in ignore_list:
            if ignored_folder in dirname:
                skip = True

        if not skip:
            for filename in filenames:
                file_list.append(os.path.join(dirname, filename))

    return file_list


def batch_copy_files(source_dir, destination_dir, files_to_copy):
    n = 0
    for source_file_path in files_to_copy:

        destination_file_path = "{}{}{}".format(
            destination_dir, "Current/",
            source_file_path[len(source_dir):])

        source_modified_date = int((datetime.datetime.fromtimestamp(os.path.
                                   getmtime(source_file_path))).
                                   strftime("%y%m%d%H%M"))
        try:
            destination_modified_date = int((datetime.datetime.fromtimestamp
                                            (os.path.getmtime
                                             (destination_file_path)))
                                            .strftime("%y%m%d%H%M"))
        except OSError:
            # Catches files which do not already exist in destination dir
            # Makes sure the destination dir
            # exists and create it if not so files can be copied
            destination_file_folder = os.path.split(destination_file_path)[0]
            if not os.path.exists(destination_file_folder):
                os.makedirs(destination_file_folder)
            copy_file(source_file_path, destination_file_path)
            n += 1
        else:
            # Only want to replace the file if the source file is newer
            if (source_modified_date > destination_modified_date):
                archive_file(source_dir, destination_dir,
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


def archive_file(source_dir, destination_dir, source_file_path,
                 destination_file_path, source_modified_date):
    archive_path = "{}{}{}-{}".format(destination_dir, "Archive/",
                                      source_file_path[len(source_dir):],
                                      source_modified_date)
    shutil.move(destination_file_path, archive_path)


def update_log(num_copied_files):
    with open("log", "a") as f:
        f.write("Backup made on {}\n".format(datetime.datetime.now().
                                             strftime("%d/%m/%y at %H:%M")))
        f.write("{} files backed up\n\n".format(num_copied_files))


if __name__ == "__main__":
    main()