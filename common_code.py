
def read_json_file_dict(json_path):
    '''
    Reads the json file and returns the dict
    '''
    with open(json_path, "r") as loaded_json_file:
        try:
            json_as_dict = json.load(loaded_json_file)
        except ValueError:
            json_as_dict = {}
    return json_as_dict


def save_json_file(loaded_json_file, json_as_dict):
    '''
    Save the master log file, overwriting the previous master log with the new data.
    '''
    try:
        loaded_json_file.seek(0)
        loaded_json_file.truncate()
        json.dump(json_as_dict, loaded_json_file, indent=4, sort_keys=True)
    except Exception as e:
        print(e)
        print("Error: Failure to save new master log file.")
    finally:
        release_file(loaded_json_file)


def create_directory(dir_path):
    '''
    Attempts to create a directory in the given path. If directory is already present,
    checks for write permissions for that directory and throws a warning if disk is
    non writable. By default, the script returns the DAASS_Scratch folder if write
    permissions were absent.
    # TODO: Default directory must be changed to something else
    '''
    # Check if directory is present
    if not os.path.isdir(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
            return dir_path

        except Exception as e:
            print("Permission denied to create directory.\n", e)
            return None

    # TODO: what would one do if this dir_path has no user write permissions
    return dir_path



def file_exists_check(filename):
    '''
    Checks if the file already exists and returns a new filename if there exists one already with an '_1', '_2' and so on.

    @filename	: full path of the file to be checked
    @returns	: full file path that is available
    '''
    new_filename = filename
    if os.path.exists(filename):
        fpath = os.path.dirname(filename)	#full directory path of the file
        fn = os.path.splitext(filename)[0]	#obtain only the file path without the extension
        fext = os.path.splitext(filename)[1]	#obtain the file extension
        all_files_prefixed = [file for file in os.listdir(fpath) if file.startswith(os.path.splitext(os.path.basename(fn))[0]) and file.endswith(fext)]	#obtain all filenames that are prefixed with the same filename
        new_filename = fn + "_" + str(len(all_files_prefixed)) + fext	#new file name will be +1 of the file extension
        if os.path.exists(new_filename):
            new_filename = fn + "_" + str(int(time.time())) + fext

        # print('Image file already exists, creating a new one - ' + new_filename)

    return new_filename

def search_recursive_file_type(root_dir, extensions, max_depth=10, relative=False):
    """
    Retrun the first file found recursively within directory matching requested file type(s)
    """
    results = list()
    for root, dirnames, filenames in os.walk(os.path.realpath(root_dir)):
        # Clear the current directory list if we have already reached the max recursion depth
        if root.count(os.sep) >= (max_depth + root_dir.count(os.sep)):
            del dirnames[:]
        # search filenames in this dir/subdir for appropriate file extensions
        for ext in extensions:
            # note that the fnmatch.filter function uses wildcards but not regex
            for filename in fnmatch.filter(filenames, '*' + ext):
                # return because we want just one match per directory, don't care which of the matches if multiple
                results.append(os.path.join(root, filename))
    if relative:
        for i, path in enumerate(results):
            results[i] = path.replace(root_dir, "")

    return results


def dict_to_json_file(data_dict, saveas_path):
    '''
    Saves the given dict as a json file
    '''
    with open(saveas_path, 'w') as file_dump:
        json.dump(data_dict, file_dump, indent=4, sort_keys=True)

    return 0

def object_to_pickle_file(thing, saveas_path):
    '''
    Saves the obj as a pickled file
    '''
    try:
        pickle_file = open(saveas_path, "wb")
        pickle.dump(thing, pickle_file)
    finally:
        pickle_file.close()

# Test: Skip, is itself for testing/debugging
def print_to_file(text, clear = False):
    print(text)
    title = PATH_SCRATCH + "/debug_prints.txt"
    method = "w" if clear else "a"
    text_file = open(title, method)
    text_file.write("\n" + text)
    text_file.close()




# def logging_wrapper(func):
#     def run_stuff(*args, **kwargs):
#         global log
#         from common import _common_log as log
#         ret = func(*args, **kwargs)
#         log.report()
#         return ret
#     return run_stuff

# EXAMPLE

# time_log = common._common_log
# time_log.clear()
# time_log.add("progress button clicked")
# <some other function>
# time_log.add("ran <some other function>")
# <some other function>
# time_log.add("ran <some other function>")
# time_log.report()

# Test: Skip, is itself for testing/debugging
class time_log():
    def __init__(self, name, cutoff = 0):
        self.name = name
        t_n = time.clock()
        self.t_init = t_n
        self.t_log = t_n
        self.log = "="*80 + "\n\nPerformamnce Log: " + name + "\n\n" + "="*80
        session.BetaSetVariable("time_log", pickle.dumps(self))
        self.records = {}
        self.cutoff = 0

    def add(self, text):
        t_n = time.clock()
        t_t = t_n - self.t_init
        t_L = t_n - self.t_log
        if t_L > self.cutoff:
            self.log += "\n\n" + "\n".join([text, "total time: " +  str(t_t), "since last: " +  str(t_L)])
        self.t_log = t_n
        try:
            self.records[text].append(t_L)
            mean = sum(self.records[text])/(len(self.records[text]))
            if t_L > self.cutoff:
                self.log += "\naverage: " + str(mean)
        except KeyError:
            self.records[text] = [t_L]

    def clear(self):
        t_n = time.clock()
        self.t_init = t_n
        self.t_log = t_n
        self.records = {}
        self.log = "="*80 + "\n\nPerformamnce Log: " + self.name + "\n\n" + "="*80

    def report(self, dump = True, save = False):
        t_n = time.clock()
        t_t = t_n - self.t_init
        t_L = t_n - self.t_log
        self.log += "\n\n" + "\n".join(["LOG REPORT END TIME: ", "total time: " +  str(t_t), "since last: " +  str(t_L)])
        self.log += "\n" + "="*80 + "\n\nEND LOG: " + self.name + "\n\n" + "="*80
        if dump:
            print(self.log)
        if save:
            title = PATH_SCRATCH + "/time_log_" + self.name + "_" + get_timestamps() + ".txt"
            text_file = open(title, "w")
            text_file.write(self.log)
            text_file.close()



#MATRIX STUFF
def normal_of_3_nodes(nodes):
    x0, y0, z0 = base.Cog( nodes[0] )
    xa, ya, za = base.Cog( nodes[1] )
    xb, yb, zb = base.Cog( nodes[2] )
    a = [xa - x0, ya - y0, za - z0]
    b = [xb - x0, yb - y0, zb - z0]
    return cross(unit_vector(a), unit_vector(b))

def unit_vector(a):
    u, v, w = a
    L = (u**2.0 + v**2.0 + w**2.0)**(0.5)
    u = u/L; v = v/L; w = w/L
    return [u, v, w]

def rotation_between(vi, vf):

    u, v, w = cross( vi, vf )
    rsin = (u**2.0 + v**2.0 + w**2.0)**(0.5)
    rcos = dot( vi, vf )

    rot_matrix = [
        [1.0, 0, 0, 0],
        [0, 1.0, 0, 0],
        [0, 0, 1.0, 0],
        [0, 0, 0, 1.0],
        ]

    rot_matrix[0][0] =      rcos + u*u*(1-rcos);
    rot_matrix[1][0] =  w * rsin + v*u*(1-rcos);
    rot_matrix[2][0] = -v * rsin + w*u*(1-rcos);
    rot_matrix[0][1] = -w * rsin + u*v*(1-rcos);
    rot_matrix[1][1] =      rcos + v*v*(1-rcos);
    rot_matrix[2][1] =  u * rsin + w*v*(1-rcos);
    rot_matrix[0][2] =  v * rsin + u*w*(1-rcos);
    rot_matrix[1][2] = -u * rsin + v*w*(1-rcos);
    rot_matrix[2][2] =      rcos + w*w*(1-rcos);

    return rot_matrix

def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]

    return c

def dot(a, b):
    c = sum( [a[i]*b[i] for i in range(len(b))] )

    return c


def print_dict(in_dict):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(in_dict)



# TIMESTAMP TOOLS

#global timezone offsets
_PT = datetime.timedelta(hours=7)

def get_timestamps(seconds = True, local = False):
    utc_time = datetime.datetime.utcnow()
    date_formatter = "%y%m%d_%H%M"
    if seconds:
        date_formatter += "%S"
    utc_timestamp = utc_time.strftime(date_formatter)
    return utc_timestamp

def get_date_offset_timestamp(utc_timestamp):
    file_time = datetime.datetime.strptime(utc_timestamp, "%y%m%d_%H%M%S")
    dtna_time = file_time - _PT
    return dtna_time.strftime("%m/%d/%y")

def get_time_offset_timestamp(utc_timestamp):
    file_time = datetime.datetime.strptime(utc_timestamp, "%y%m%d_%H%M%S")
    dtna_time = file_time - _PT
    return dtna_time.strftime("%H:%M")