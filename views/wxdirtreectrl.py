"""wxdirtreectrl.py - subclass of wxPython's TreeCtrl providing additional functions for
lists of directories

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import wx
import os
import os.path

class DirTreeCtrl(wx.TreeCtrl):
    """Subclass of wx.TreeCtrl designed to handle folders and subfolders"""

    def __init__(self, *args, **kwargs):
        super(DirTreeCtrl, self).__init__(*args, **kwargs)
        self.root = self.AddRoot(text="Selected Folders")
        self.folders = {}

    def list_folders(self, parent_folder, relative=True):
        """Returns a list of all the sub-folders found under the parent folder.
        If relative is True (default), paths are stored relative to this parent folder's path;
        otherwise the full path is stored."""
        folders = []
        if os.path.isdir(parent_folder):
            for root, dirs, files in os.walk(parent_folder):
                for fldr in dirs:
                    path = os.path.join(root, fldr)
                    if relative:
                        path = os.path.relpath(path, start=parent_folder)
                    folders.append(os.path.normcase(path))
        return folders

    def add_folder(self, folder_path):
        """Adds the specified folder_path and all its sub-folders to the tree as a new item"""
        new_entry = self.AppendItem(parent=self.GetRootItem(), text=folder_path)
        sub_folders = self.list_folders(folder_path)
        self.folders[folder_path] = sub_folders
        self.populate_tree()

    def remove_folder(self):
        """Removes the currently selected folder (if any)."""
        selected_folder = self.GetSelection()
        if selected_folder.IsOk():
            selected_folder_name = self.GetItemText(selected_folder)
            if selected_folder_name in self.folders:
                self.folders.pop(selected_folder_name)
            else:
                for fldr in self.folders:
                    if selected_folder_name in self.folders[fldr]:
                        self.folders[fldr].pop(self.folders[fldr].index(selected_folder_name))
                        break
        self.populate_tree()
        if selected_folder.IsOk():
            self.Expand(self.GetItemParent(selected_folder))

    def populate_tree(self):
        self.DeleteChildren(self.root)
        for folder, sub_folders in self.folders.iteritems():
            new_entry = self.AppendItem(self.root, folder)
            if len(sub_folders) != 0:
                for fldr in sub_folders:
                    self.AppendItem(parent=new_entry, text=fldr)
        self.SortChildren(self.root)
        self.Refresh()

    def selected_folders(self):
        """Returns a list of the folder and its subfolders currently selected"""
        folders = []
        selected_folder = self.GetSelection()
        if selected_folder.IsOk():
            selected_folder_name = self.GetItemText(selected_folder)
            if selected_folder_name in self.folders:
                folders.append(selected_folder_name)
                folders.extend([os.path.join(selected_folder_name, fldr) for fldr in self.folders[selected_folder_name]])
            else:
                for fldr in self.folders:
                    if selected_folder_name in self.folders[fldr]:
                        full_path = os.path.join(fldr, selected_folder_name)
                        folders.append(full_path)
        return folders

    def get_folders(self):
        """Returns a list of all the folders and subfolders"""
        folders = []
        for folder in self.folders:
            folders.append(folder)
            folders.extend([os.path.join(folder, fldr) for fldr in self.folders[folder]])
        return folders