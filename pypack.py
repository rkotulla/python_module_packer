#!/usr/bin/env python

import os, sys, numpy
import scipy.stats, scipy.special
import scipy

import types

sys.path.append("/work/podi_prep56")
import podi_sitesetup as ss
import podi_imcombine

#sys.modules.keys()
#for x in sys.modules: #.keys():
#    print x, type(x)

# modulenames = set(sys.modules)&set(globals())
# allmodules = [sys.modules[name] for name in modulenames]
# for am in allmodules:
#     print am, type(am)
#     print am.globals()

import modulefinder


if __name__ == "__main__":

    # Start the code you want to study
    mf = modulefinder.ModuleFinder()
    mf.run_script([
        "/work/podi_devel/podi_imcombine.py",
        "/work/podi_devel/podi_collectcells.py",
    ])
    #mf.report()


    # # get list of modules
    # modules = []
    # for name, val in globals().items():
    #     print
    #     if isinstance(val, types.ModuleType):
    #         print val.__name__
    #         try:
    #             print "PATH:", val.__path__,"\n",
    #         except:
    #             pass

    #         try:
    #             print "FILE:", val.__file__,"\n",
    #         except:
    #             pass

    #         modules.append(val)

    master_modules = []
    modules = []
    for mod in mf.modules:
        modules.append(mod)
        mod_parts = mod.split(".")
        master_modules.append(mod_parts[0])

    print modules
    print type(modules)
    modules.sort()
    print "\n".join(modules)

    print "------------------------------------"
    
    master_modules = list(set(master_modules))
    master_modules.sort()
    print "\n".join(master_modules)

#    sys.exit(0)

    #
    # Now create a tar-file with all files we might need
    #
    import tarfile, glob

    # def reset(tarinfo):
    #     tarinfo.uid = tarinfo.gid = 0
    #     tarinfo.uname = tarinfo.gname = "root"
    #     return tarinfo

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
            print "HARDLINK:", tarinfo.type, tarinfo.linkname
            tarinfo.type = tarfile.REGTYPE
            #return None
            
        # elif (tarinfo.isdev()):
        #     print "Removing devics (block device, character device, or FIFO"
        #     return None
        # elif (tarinfo.issym()):
        #     print "This is a symbolic link"
        #     return None

        if (tarinfo.name.startswith(master_dir)):
            tarinfo.name = tarinfo.name[len(master_dir):]
        tarinfo.uname = tarinfo.gname = 'everyone'
        #print master_dir, "---", tarinfo.name, len(master_dir)
        return tarinfo


    tar = tarfile.open("sample.tar.gz", "w:gz")

    add_files = True #False
    if (add_files):
        print "\n\n\nAdding files to tar file"
        # Now add all files we might need for each of the modules
        for module_name in master_modules:
            module = mf.modules[module_name]
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

