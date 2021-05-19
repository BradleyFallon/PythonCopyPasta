# PYTHON script

###############################################################################
#                Copyright Daimler Trucks North America,                      #
#                2016 All Rights Reserved                                     #
#                UNPUBLISHED, LICENSED SOFTWARE.                              #
#                                                                             #
#                CONFIDENTIAL AND PROPRIETARY INFORMATION                     #
#                WHICH IS THE PROPERTY OF DAIMLER TRUCKS N.A.                 #
###############################################################################

"""
Welcome to the Task and Monitor library!
Enjoy!

class Monitor: Contains task objects. Monitors and runs the associated commands.
class Task: Contains info about a script to be executed and its status

The purpose of the monitor and task classes is to be able to define a scripted workflow that can be automated and
also has the ability to be interrupted and resumed.
"""

import os
import sys
import time
import subprocess
import datetime
import json

# If launched as a standalone script, we still want ability to reference the daass package
daass_path = os.path.abspath(__file__)
while not os.path.basename(daass_path) == "daass":
    daass_path = os.path.dirname(daass_path)
ansa_auto_path = os.path.dirname(daass_path)
sys.path.append(ansa_auto_path)

DEBUG_TASK_KEY = "DEBUG"

from daass.shared import file_utils


class Monitor(object):
    """
    Contains task objects. Monitors and runs the associated commands.
    """

    # Formatting for printing to terminal
    HEADER = "STATUS      TASK                            Result/Info"
    TEMPLATE = "{:12}{:32}{}"
    # This is not really a rate, but an inverse rate. This is the sleep time.
    REFRESH_RATE = 5

    # The environment variable name for the log path
    LOG_DUMP = "MONITOR_LOG_DUMP_PATH"
    LOG_JSON = "MONITOR_LOG_JSON_PATH"

    # Logging dict keys
    _KEY_LOG = "info_log"
    _KEY_CMD = "command"
    _KEY_MESSAGE = "message"
    _KEY_TIMESTAMP = "timestamp"
    _KEY_STATUS = "status"

    def __init__(self, workflow_name, logging_dir, refresh_timestamp=None):
        self.name = workflow_name
        self.refresh_timestamp = refresh_timestamp

        # This is the log where all prints go for general debugging needs
        # This is for developer use only (but could potentially be used for error detection)
        self.log_dump_dir = os.path.join(logging_dir, "task_logs")
        self.log_testing = os.path.join(logging_dir, "error_summary.txt")
        file_utils.create_directory(self.log_dump_dir)
        # This is a clean json formatted log for showing status to the user
        # This is for user's gui info and no debugging stuff belongs here
        self.log_json_path = os.path.join(logging_dir, file_utils.clean_filename(workflow_name) + ".json")

        # This is setting the log path variable for all python subprocesses launched by this monitor
        # This is to be used by the class method log_string
        os.environ[self.LOG_JSON] = self.log_json_path

        self.tasks = list()
        self.active_task_indexs = set()
        self.complete_task_indexs = set()
        self.failed_task_indexs = set()

        self.cursor = None

    def add_task(self, task):
        next_index = len(self.tasks)
        self.tasks.append(task)
        return next_index

    def init_json_log(self):
        logs_json_dict = dict()
        if os.path.isfile(self.log_json_path):
            logs_json_dict_old = file_utils.read_json_file_dict(self.log_json_path)

            # If a refresh timestamp was provided, then do not use old data unless timestamp is a match
            # If no refresh, then always use the old json data if it exists
            if self.refresh_timestamp:
                if self._KEY_TIMESTAMP in logs_json_dict_old:
                    if logs_json_dict_old[self._KEY_TIMESTAMP] == self.refresh_timestamp:
                        logs_json_dict = logs_json_dict_old
            else:
                logs_json_dict = logs_json_dict_old

            for task in self.tasks:
                try:
                    task.status = logs_json_dict[task.name][self._KEY_STATUS]
                    # In the case file does not exist, or is inaccessable, or is missing keys
                    # Then recreate a new one
                except KeyError:
                    pass
        else:
            pass

        for task in self.tasks:
            if not task.name in logs_json_dict:
                logs_json_dict[task.name] = {
                    self._KEY_LOG: list(),
                    self._KEY_CMD: task.exec_os_command,
                    self._KEY_STATUS: task.status,
                }
        with open(self.log_json_path, 'w') as f:
            json.dump(logs_json_dict, f, indent=4)


    def error_log(self, *arg):
        print(*arg, file=sys.stderr)
        return
        # # Start the dump log
        # with open(self.log_dump_path, 'a+') as sys.stdout:
        #     print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        #     print(*arg)
        # # Need to reset sys.stdout after back to default
        # sys.stdout = sys.__stdout__

    def start(self):
        """
        Take over console for status monitoring, check status of all tasks, then monitor and run all incomplete tasks.
        """

        self.init_json_log()

        try:
            for task in self.tasks:
                if task.status == Task.DONE or task.status == Task.SKIP:
                    self.complete_task_indexs.add(task.index)
                    self.active_task_indexs.discard(task.index)
                elif task.status == Task.FAILED or task.status == Task.CANCELED:
                    self.failed_task_indexs.add(task.index)
                    self.active_task_indexs.discard(task.index)

            # Check if tasks are complete.
            for task in self.tasks:
                if task.status == Task.WAIT or task.status == Task.ACTIVE:
                    task.update()

            # Launch all tasks that are not complete if the prerequisites are complete
            for task in self.tasks:
                if task.status == task.WAIT and task.is_ready():
                    task.launch()
                    time.sleep(2) # Stagger launches

            # Until broken, check if current task is complete.
            # If current task is complete, launch and monitor the next task if it exists.
            # Stop looping when the set of completed tasks is as long as the task list
            while len(self.complete_task_indexs) < len(self.tasks):
                self.print_status()
                time.sleep(self.REFRESH_RATE)

                # For all sctive tasks, check if they are complete
                active_tasks = [self.tasks[i] for i in self.active_task_indexs]
                for active_task in active_tasks:
                    active_task.update()

                # For all queued tasks, launch if they are now ready
                queued_tasks = [task for task in self.tasks if task.index not in self.complete_task_indexs|self.active_task_indexs|self.failed_task_indexs]
                for task in queued_tasks:
                    if task.is_ready():
                        task.launch()
                        time.sleep(2) # Stagger launches
                    elif task.is_canceled():
                        task.set_status(task.CANCELED)

        except:
            # End the monitor and restore the terminal to its original operating mode
            import traceback
            err = sys.exc_info()
            tb = traceback.format_exc()
            print(err, file=sys.stderr)
            print(tb, file=sys.stderr)

        else:
            # Print final status to terminal and wait a while before shutting down the monitor
            self.print_status()

        finally:
            # End the monitor and restore the terminal to its original operating mode
            exit()


    def print_status(self):
        """
        Print a status table in the console.
        This will clear the terminal and print from the top left.
        """

        # Get the terminal current window size and update the cursor object to be aware of this
        w_height, w_width = os.popen('stty size', 'r').read().split()
        w_height = int(w_height)
        w_width = int(w_width)

        print("\n"*(w_height+5))
        print(self.name.upper())
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(self.HEADER)
        lines_written = 3
        for task in self.tasks:
            lines_written += 2
            if lines_written <= w_height:
                print("")
                text = self.TEMPLATE.format(task.status, task.name, task.info)
                text = (text[:w_width-2] + '..') if len(text) > w_width else text
                print(text)
            else:
                # This is meant to be in case there is not room to print more lines, stop printing
                continue
        if lines_written < w_height: 
            print('\n'*(w_height-(lines_written+2)))

    @classmethod
    def log_string(cls, message, task_key=None):
        """
        This writes a message to the monitor log. Rather than using an instance Monitor object to get the log path,
        the system environment variable is used, so that this can be called by importing Monitor with no need to retain a reference
        to the active monitor object.
        """
        try:
            if os.environ[cls.LOG_JSON] and task_key:
                logs_json_fie, logs_json_dict = file_utils.checkout_json_file(os.environ[cls.LOG_JSON])

                try:
                    logs_json_dict[task_key][cls._KEY_LOG].append(
                        {
                            cls._KEY_MESSAGE: message,
                            cls._KEY_TIMESTAMP: datetime.datetime.now().strftime('%m/%d %H:%M:%S')
                        }
                    )
                    file_utils.save_json_file(logs_json_fie, logs_json_dict)

                except KeyError:
                    if task_key == DEBUG_TASK_KEY:
                        logs_json_dict[task_key] = {
                            cls._KEY_LOG: [
                                {
                                    cls._KEY_MESSAGE: message,
                                    cls._KEY_TIMESTAMP: datetime.datetime.now().strftime('%m/%d %H:%M:%S'),
                                },
                            ],
                        }
                        file_utils.save_json_file(logs_json_fie, logs_json_dict)

                finally:
                    file_utils.release_file(logs_json_fie)

            else:
                print(message)
        except:
            print(message)


class Task(object):
    """
    Contains info about a script to be executed and its status.
    """

    # Status codes
    DONE = "Done."
    SKIP = "n/a"
    FAILED = "Failed!"
    ACTIVE = "Active..."
    WAIT = "...Queued"
    CANCELED = "Canceled."


    def __init__(self, monitor, name, exec_os_command, check_if_done_fn, check_if_skip_fn=None, prereq_indexs=None, cancel_if_fail_indexs=None, timeout=12000):

        ##############################################
        # Dependent on input properties
        ##############################################
        self.monitor = monitor
        self.name = name
        self.exec_os_command = exec_os_command
        self.check_if_done_fn = check_if_done_fn
        self.check_if_skip_fn = check_if_skip_fn
        # This is required to find log messages for status info
        # Must define the logging key in the task's script and maintain uniqueness manually
        self.timeout = timeout

        self.log_err_path = os.path.join(monitor.log_dump_dir, file_utils.clean_filename(name) + ".err")
        self.log_out_path = os.path.join(monitor.log_dump_dir, file_utils.clean_filename(name) + ".out")

        # This could be used to manage parallel tasks
        if prereq_indexs is None:
            prereq_indexs = set()
        self.prereq_indexs = set(prereq_indexs)

        # This could be used to cancel tasks if a specific set of predecessors failed.
        if cancel_if_fail_indexs is None:
            cancel_if_fail_indexs = set(self.prereq_indexs)
        self.cancel_if_fail_indexs = set(cancel_if_fail_indexs)

        # Standard starting state properties
        # Status is to be a status from the set of standard task statuses
        self.status = self.WAIT
        # Info is a string of whatever extra notes the user should see about the status of the task
        self.info = "..."
        self.launched_time = None

        # Add self to the parent monitor's task list
        self.index = monitor.add_task(self)
        self.process = None

    # def init_dump_log(self):
    #     # Start the dump log
    #     with open(self.log_dump_path, 'a+') as sys.stdout:
    #         print("\n")
    #         print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #         print("New " + self.name + " started.")
    #     # Need to reset sys.stdout after back to default
    #     sys.stdout = sys.__stdout__

    def set_status(self, status_code):
        """
        Set status attribute and save to json log
        """
        self.status = status_code
        json_log_file, log_dict = file_utils.checkout_json_file(self.monitor.log_json_path)
        log_dict[self.name][self.monitor._KEY_STATUS] = self.status
        file_utils.save_json_file(json_log_file, log_dict)

        if self.status == Task.DONE or self.status == Task.SKIP:
            self.monitor.complete_task_indexs.add(self.index)
            self.monitor.active_task_indexs.discard(self.index)
        elif self.status == Task.FAILED or self.status == Task.CANCELED:
            self.monitor.failed_task_indexs.add(self.index)
            self.monitor.active_task_indexs.discard(self.index)

    def find_error_in_log(self):
        error_found = False
        with open(self.log_err_path , 'r') as f_err:
            line = f_err.readline()
            while line:
                if "Error:" in line:
                    with open(self.monitor.log_testing , 'a+') as f_dump:
                        f_dump.write("\n\n" + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
                        f_dump.write(self.name + "\n")
                        f_dump.write(line)
                        f_dump.write("For more info see file:\n")
                        f_dump.write(self.log_err_path)
                        error_found = True
                line = f_err.readline()
        return error_found

    # def log_output(self):
    #     '''
    #     Logs the output to the log_file defined in the monitor class
    #     '''
    #     try:
    #         output = self.process.communicate()
    #         output_str = "\n".join([
    #             out.decode('utf-8') for out in output if out is not None
    #         ])
    #         self.monitor.error_log(self.name + " : RETURNED: " + str(self.process.poll()) + " : " + output_str)

    #         # The command above will wait for a process to be complete, if we decided we need to check before that, then
    #         # the following may be a start
    #         # line = self.process.stdout.readline()
    #         # self.monitor.error_log(self.name + " : " + line)

    #     except:
    #         # NOTE: we must actually understand what's happening here.. if the try/except statement is removed
    #         # then we will notice an error because of the subprocess.communicate() method.
    #         pass

    def update(self):

        # TODO: What if self.process is None, becuase the monitor was closed and resumed...?

        if self.is_canceled():
            self.set_status(self.CANCELED)

        elif self.is_skip():
            self.set_status(self.SKIP)

        elif self.check_if_done_fn():
            self.set_status(self.DONE)

        elif self.status == self.ACTIVE:
            if self.launched_time is None:
                self.launched_time = time.time()

            if self.process:
                return_code = self.process.poll()
                if return_code is None:
                    # Process seems to still be running, check if it has exceeded max runtime
                    if (time.time() - self.launched_time) > self.timeout:
                        self.monitor.error_log(self.name + " : Process timed out.")
                        self.set_status(self.FAILED)
                else:
                    if return_code:
                        self.set_status(self.FAILED)
                    elif self.find_error_in_log():
                        self.set_status(self.FAILED)
            # TODO: What if self.process is None, becuase the monitor was closed and resumed...?
            # else:
            #     self.set_status(self.FAILED)

        log_dict = file_utils.read_json_file_dict(self.monitor.log_json_path)
        # Make sure keys exist in json
        try:
            log_dict[self.name][self.monitor._KEY_LOG]
        except KeyError:
            self.monitor.init_json_log()
            log_dict = file_utils.read_json_file_dict(self.monitor.log_json_path)

        try:
            # Only update info message if there is at least one message
            if log_dict[self.name][self.monitor._KEY_LOG]:
                ts = log_dict[self.name][self.monitor._KEY_LOG][-1][self.monitor._KEY_TIMESTAMP]
                msg = log_dict[self.name][self.monitor._KEY_LOG][-1][self.monitor._KEY_MESSAGE]
                self.info = ts + ": " + msg
        except:
            pass

    def is_ready(self):
        # check if any items in prereqs and not in completed
        # Comparing Sets
        missing_prereqs = bool(self.prereq_indexs - self.monitor.complete_task_indexs)
        if missing_prereqs:
            return False
        else:
            # No missing_prereqs means we are ready to go
            return True

    def is_canceled(self):
        # check if any tasks failed that should cancel this task
        # Comparing Sets to get overlap of fail triggers and failed tasks
        should_cancel = bool(self.cancel_if_fail_indexs & self.monitor.failed_task_indexs)
        if should_cancel:
            return True
        else:
            return False

    def is_skip(self):
        # The check if skip function may or may not have been defined
        if self.check_if_skip_fn is not None:
            return self.check_if_skip_fn()

    def launch(self):
        self.launched_time = time.time()
        self.set_status(self.ACTIVE)

        self.monitor.active_task_indexs.add(self.index)

        if self.exec_os_command:
            command_string = self.exec_os_command
            command_list = command_string.split(" ")
            # NOTE: http://www.sharats.me/posts/the-ever-useful-and-neat-subprocess-module/
            # self.process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            with open(self.log_out_path, 'a+') as f_out, open(self.log_err_path, 'a+') as f_err:
                self.process = subprocess.Popen(command_list, stdout=f_out, stderr=f_err)

        else:
            pass
