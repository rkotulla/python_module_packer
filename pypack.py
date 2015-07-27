#!/usr/bin/env python

import os, sys
import types
import modulefinder
import optparse

if __name__ == "__main__":

    
    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="print additional output to stdout")
    (options, args) = parser.parse_args()
    #print options
    #print type(options)
    #print args

    tar_output_file = args[0]

    master_modules = []

    master_modules_dict = {}

    #
    # Now study all scripts and assemble a list of master modules
    #
    for scriptfile in args[1:]:

        # Start the code you want to study
        print("Assembling dependencies for %s" % (scriptfile))
        mf = modulefinder.ModuleFinder()
        mf.run_script(scriptfile)
        master_modules_dict.update(mf.modules)

        modules = []
        for mod in mf.modules:
            modules.append(mod)
            mod_parts = mod.split(".")
            master_modules.append(mod_parts[0])

        #print type(mf.modules)
        #print modules
        #print type(modules)
        #modules.sort()
        #print "\n".join(modules)

    #print "------------------------------------"

    master_modules = list(set(master_modules))
    master_modules.sort()
    if (options.verbose):
        print "Collecting necessary files for the following modules:"
        print " -- ","\n -- ".join(master_modules)

    #
    # Now create a tar-file with all files we might need
    #
    import tarfile, glob

    def strip_path(tarinfo):
        #print tarinfo

        # Set username to something else (most likely was 'root/root' before)
        tarinfo.uname = tarinfo.gname = 'everyone'

        # Now change the name = filename to not include the directory name
        _, bn = os.path.split(tarinfo.name)
        tarinfo.name = bn #"test/"+tarinfo.name
        return tarinfo


    master_dir = '/usr/lib'
    def strip_master_dir(tarinfo):
        if (tarinfo.islnk()):
            #print "Removing hard link from filelist"
            #print "HARDLINK:", tarinfo.type, tarinfo.linkname
            tarinfo.type = tarfile.REGTYPE

        if (tarinfo.name.startswith(master_dir)):
            tarinfo.name = tarinfo.name[len(master_dir):]
        tarinfo.uname = tarinfo.gname = 'everyone'
        #print master_dir, "---", tarinfo.name, len(master_dir)
        return tarinfo


    tar = tarfile.open(tar_output_file, "w:gz")

    add_files = True
    if (add_files):

        print "\n\n\nAdding files to tar file"
        # Now add all files we might need for each of the modules
        for module_name in master_modules:
            
            #import_cmd = "import %s as module" % (module_name)
            #exec(import_cmd)
            
            # module = mf.modules[module_name]
            module = master_modules_dict[module_name]
            try:
                _path = module.__path__
            except:
                _path = None

            try:
                _file = module.__file__
            except:
                _file = None

            #print module.__name__, _path, _file

            if (_path == None and _file != None):
                # We have only a file locator, so this is likely a single-file module
                #print "F", _file
                tar.add(_file, filter=strip_path)
            elif (_path != None):
                # We have a full path
                # Go through the directory recursively, and add all files

                md, bn = os.path.split(_path[0])
                #print "D", _path[0]
                master_dir = md[1:]+"/" #_path[0][1:]+"/"
                for root, subdirs, files in os.walk(_path[0]):
                    # for subdir in subdirs:
                    #     print('\t- subdirectory ' + subdir)
                    #print('--\nroot = ' + root)
                    #list_file_path = os.path.join(root, 'my-directory-list.txt')
                    #print('list_file_path = ' + list_file_path)

                    for filename in files:
                        file_path = os.path.join(root, filename)
                        real_path = os.path.realpath(file_path)
                        #print file_path, file_path[len(master_dir):]
                        tar.add(real_path, filter=strip_master_dir)


    #tar.add("foo", filter=reset)
    tar.close()

