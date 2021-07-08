"""
usage: linkcomics.py [-h] [-c] [-d] [-w] <source folder> <target folder>

Creates symlinks to all your comics.

positional arguments:
  <source folder>  The folder to scan for comic files.
  <target folder>  The folder to contain the links to comic files.

optional arguments:
  -h, --help       show this help message and exit
  -c, --create     Creates the symlinks in the target folder.
  -d, --delete     Deletes broken symlinks/empty directories in the target folder.
  -w, --whatif     Simulates running the command (does not make any changes).

Creates a discrete hierarchical folder structure containing links to all
comics in a comics library (folder of .cbz files), based on the metadata
in each file. The ComicInfo.xml metadata is read from each comic and a link
is then created in the target location such that the folder structure is as
follows:
    <target fodler>/Publisher/Series/Volume/Series #000 (Year-Month).cbz
Example:
    /home/user/comic_links/Marvel/X-Men/V2009/X-Men #012 (2013-09).cbz
"""

from posixpath import join
from dataclasses import dataclass
import sys
import argparse
import os
import zipfile
import xml.etree.ElementTree as ET
import re
import pathlib

@dataclass
class ComicMetadata:
    '''
    Holds a subset of the comic book metadata read from a .cbz file.
    '''
    Publisher: str = ''
    Series: str = ''
    Volume: int = ''
    Number: str = ''
    Year: int = ''
    Month: int = ''

    def Validate(self):
        '''
        Returns whether the values of "required" attributes are valid.

        The required attributes are checked to see if they are empty.
        If any of them are, this method returns False.

        Required attributes are: Publisher, Series, Volume, Number, Year.

        Returns:
            bool: The result of the check.
        '''
        if self.Publisher == '' \
            or self.Series == '' \
            or self.Volume == '' \
            or self.Number == '' \
            or self.Year == '':
            return False
        else: return True

def CleanUpLinks(folder):
    '''
    Removes broken symlinks.

    Recursively removes symlinks that no longer point to a valid file (for example, 
    due to file system operations such as when the link targets are moved, renamed, 
    or deleted).

    Args:
        folder (str): The path to the folder to clean up.
        This folder will be scanned for broken links.

    Returns:
        int: The number of symlinks that were removed.
    '''

    num_links = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root,file)
            if os.path.islink(file_path) and not os.path.exists(file_path):
                if not args.whatif: os.remove(file_path)
                num_links+=1
    return num_links

def CleanUpFolders(folder):
    '''
    Removes empty folders.

    Recursively removes all empty folders.

    Args:
        folder (str): The path to the folder to clean up.
        This folder will be scanned for empty subfolders.

    Returns:
        int: The number of folders that were removed
    '''

    num_folders = 0
    # remove empty directories
    for root, dirs, files in os.walk(folder):
        if len(dirs) == 0 and len(files) == 0:
            if not args.whatif: os.rmdir(root)
            num_folders+=1
    return num_folders

if __name__ == "__main__":
    # parse the arguments passed in at the command line
    parser = argparse.ArgumentParser(description="Creates symlinks to all your comics.")
    parser.add_argument(
        "source_folder", 
        type=pathlib.Path,
        metavar="<source folder>",
        help="The folder to scan for comic files.")
    parser.add_argument(
        "target_folder", 
        type=pathlib.Path,
        metavar="<target folder>",
        help="The folder to contain the links to comic files.")
    parser.add_argument(
        "-c",
        "--create", 
        action="store_true",
        help="Creates symlinks in the target folder.",)
    parser.add_argument(
        "-d",
        "--delete", 
        action="store_true",
        help="Deletes broken symlinks/empty directories in the target folder.")
    parser.add_argument(
        "-w",
        "--whatif", 
        action="store_true",
        help="Simulates running the command (does not make any changes).")
    args = parser.parse_args()
    if not args.delete and not args.create: parser.print_help(); exit()

    if args.delete:
        deleted_links = CleanUpLinks(args.target_folder)
        print(f"{deleted_links} broken links deleted.")
        deleted_folders = CleanUpFolders(args.target_folder)
        print(f"{deleted_folders} empty folders deleted.")
    
    if not args.create: exit()
    # traverse the folder for cbz files
    for root, dirs, files in os.walk(args.source_folder):
        for file in files:
            cbz_path = os.path.join(root,file)
            if not file.endswith(".cbz"): continue

            # open the cbz comic
            try: cbz = zipfile.ZipFile(cbz_path)
            except zipfile.BadZipFile: print(f"ZIP_ERROR: {cbz_path}"); continue
            if not "ComicInfo.xml" in cbz.namelist(): print(f"XML_NOT_FOUND: {cbz_path}"); continue

            # read and store the metadata from the .cbz
            comic_info = cbz.open("ComicInfo.xml")
            root_node = ET.parse(comic_info).getroot()
            metadata = ComicMetadata()
            for key in ComicMetadata.__dataclass_fields__:
                element = root_node.find(key)
                if element is not None:
                    metadata.__setattr__(key, element.text)
            if not metadata.Validate():
                print(f"INCOMPLETE_METADATA: {cbz_path}"); continue

            #clean up invalid/unwanted characters. some are replaced with a dash, some are removed,
            #some are replaced with a more friendly equivalent
            metadata.Series = re.sub('[\\/:;]',' - ',metadata.Series)
            metadata.Series = re.sub("[?,']",'',metadata.Series)
            metadata.Series = re.sub("\s{2,}"," ",metadata.Series)
            metadata.Number = metadata.Number.replace("½",".5").replace("A",".1").replace("B",".2").replace("/","-")

            #compile the location and name of the symlink
            target_folder = os.path.join(
                args.target_folder,
                metadata.Publisher,
                metadata.Series,
                f"V{metadata.Volume}"
            )
            file_name = "{0} #{1:0>3} ({2}{3}{4:0>2}).cbz".format(
                metadata.Series,
                metadata.Number,
                metadata.Year,
                "-" if metadata.Month else "",
                metadata.Month if metadata.Month else ""
            )
            sym_link = os.path.join(target_folder, file_name)

            # create the folder if necessary
            if not args.whatif: os.makedirs(target_folder, exist_ok=True)

            # create the link
            if not args.whatif:
                try: 
                    if not os.path.exists(sym_link): os.symlink(cbz_path, sym_link)
                except: print(f"SYMLINK_ERROR: {cbz_path} -> {sym_link}")
            else: print(f"{sym_link}")