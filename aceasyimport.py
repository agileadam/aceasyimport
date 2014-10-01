#!/usr/bin/env python
import argparse
from ConfigParser import SafeConfigParser
import datetime
import logging
import os.path
import re
import requests
import sys

api_token = ''
api_url = ''

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

# File logging
#fh = logging.FileHandler("result.log")
#fh.setLevel(logging.DEBUG)
#fh.setFormatter(formatter)
#LOG.addHandler(fh)

# Console logging
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
LOG.addHandler(ch)

parser = argparse.ArgumentParser(description='EasyImport for Active Collab 3', version='2.0', add_help=True)
parser.add_argument('inputfile', action="store", type=file)
args = parser.parse_args()

configfile_path = os.path.join(os.path.expanduser('~'), '.aceasyimportconfig')


def process_config(configfile_path):
    global api_token
    global api_url

    parser = SafeConfigParser()
    parser.read(configfile_path)

    error_count = 0

    potential_api_url = parser.get('api_settings', 'api_url')
    if potential_api_url == '':
        LOG.error('Configuration file needs valid api_url')
        error_count += 1
    else:
        api_url = potential_api_url

    potential_api_token = parser.get('api_settings', 'api_token')
    if potential_api_token == "":
        LOG.error('Configuration file needs valid api_token')
        error_count += 1
    else:
        api_token = potential_api_token

    if error_count > 0:
        sys.exit()


def write_blank_config():
    try:
        with open(configfile_path, 'w') as configfile:
            configfile.write("[api_settings]\n")
            configfile.write("api_url = \n")
            configfile.write("api_token = ")
    except IOError:
        # TODO provide instruction on config file
        LOG.error('Could not create template config file.')
        sys.exit()


try:
    with open(configfile_path) as configfile:
        # The file exists, so process it (note that we're passing the path, not the file object)
        process_config(configfile_path)
except IOError:
    write_blank_config()
    LOG.warning('No config file found; created one. Please edit "%s" and try again.' % configfile_path)
    sys.exit()


def make_get_request(path_info, parameters=None):
    if parameters is None:
        parameters = {}
    parameters['auth_api_token'] = api_token
    parameters['format'] = 'json'
    parameters['path_info'] = path_info
    r = requests.get(api_url, params=parameters, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        return {}


def make_post_request(path_info, data_payload, parameters=None):
    if parameters is None:
        parameters = {}
    parameters['auth_api_token'] = api_token
    parameters['format'] = 'json'
    parameters['path_info'] = path_info
    r = requests.post(api_url, params=parameters, data=data_payload, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        return {}


def all_projects():
    result = make_get_request('projects')
    all = dict()
    for project in result:
        all[project['id']] = project['name']
    return all


def project_milestones(project_id):
    result = make_get_request('projects/' + str(project_id) + '/milestones')
    all_milestones = dict()
    if result:
        for milestone in result:
            all_milestones[milestone['id']] = milestone['name']
    return all_milestones


def project_tasks(project_id):
    # Returns open and closed tasks that are not archived
    result = make_get_request('projects/' + str(project_id) + '/tasks')
    all_tasks = dict()
    if result:
        for task in result:
            # Use the task_id (relative to the project), not the id (database unique task ID)
            all_tasks[task['task_id']] = {'name': task['name'], 'milestone_id': task['milestone_id']}
    return all_tasks


def task_subtasks(project_id, task_id):
    result = make_get_request('projects/' + str(project_id) + '/tasks/' + str(task_id) + '/subtasks')
    all_subtasks = dict()
    if result:
        for subtask in result:
            all_subtasks[subtask['id']] = subtask['name']
    return all_subtasks


def find_project_by_name(search_name, projects):
    for id, name in projects.items():
        if search_name.lower() == name.lower():
            return id
    return 0


def find_milestone_by_name(search_name, milestones):
    for id, name in milestones.items():
        if search_name.lower() == name.lower():
            return id
    return 0


def find_task_by_name(milestone_id, search_name, tasks):
    for id, task in tasks.items():
        if search_name.lower() == task['name'].lower():
            # We have a match on name only
            # If we're checking within a specific milestone, make sure we're limiting to only this milestone
            if milestone_id > 0:
                if milestone_id == task['milestone_id']:
                    return id
            else:
                return id
    return 0


def find_subtask_by_name(search_name, subtasks):
    for id, name in subtasks.items():
        if search_name.lower() == name.lower():
            return id
    return 0


def create_milestone(project_id, name, attributes):
    valid_keys = ['name', 'body', 'start_on', 'priority', \
                 'assignee_id', 'other_assignees', 'due_on']
    data = dict()
    data['submitted'] = 'submitted'
    data['milestone[name]'] = name
    data['milestone[priority]'] = 0

    # Milestones REQUIRE "start_on" and "due_on" dates;
    # Set a default start on date of today, and a due on of 1 year from today
    # These will be overwritten if valid values are found in attribute handling
    start_date = datetime.datetime.now()
    end_date = start_date + datetime.timedelta(days=365)
    data['milestone[start_on]'] = start_date.strftime('%Y-%m-%d')
    data['milestone[due_on]'] = end_date.strftime('%Y-%m-%d')

    for key, val in attributes.items():
        if key in valid_keys:
            data['milestone[' + key + ']'] = val
    result = make_post_request('projects/%d/milestones/add' % project_id, data)
    return result


def create_task(project_id, milestone_id, name, attributes):
    valid_keys = ['name', 'body', 'visibility', 'category_id', 'label_id', \
                 'milestone_id', 'priority', 'assignee_id', 'other_assignees', 'due_on']
    data = dict()
    data['submitted'] = 'submitted'
    data['task[name]'] = name
    data['task[priority]'] = 0
    data['task[label_id]'] = 0
    if milestone_id <> 0:
        data['task[milestone_id]'] = milestone_id
    for key, val in attributes.items():
        if key in valid_keys:
            data['task[' + key + ']'] = val
    result = make_post_request('projects/%d/tasks/add' % project_id, data)
    return result


def create_subtask(project_id, task_id, name, attributes):
    valid_keys = ['body', 'assignee_id', 'priority', 'label_id', 'due_on']
    data = dict()
    data['submitted'] = 'submitted'
    data['subtask[body]'] = name
    data['subtask[priority]'] = 0
    data['subtask[label_id]'] = 0
    for key, val in attributes.items():
        if key in valid_keys:
            data['subtask[' + key + ']'] = val
    result = make_post_request('projects/%d/tasks/%d/subtasks/add' %
                               (project_id, task_id), data)
    return result

# First, we need a dictionary of all projects (id, name)
projects = all_projects()

# We need these outside of the loop so we can reduce API queries
# because we should only need to lookup a specific project's milestones/tasks once
project_id = 0
milestone_id = 0
milestones = dict()
tasks = dict()
error_count = 0
warning_count = 0

# loop through all of the lines in the input file and process them
lines = args.inputfile.read().splitlines()

i = 0
for line in lines:
    # Increase the line number by one for our user messages
    i += 1

    # Strip off beginning hyphen and space chars
    lineclean = line.lstrip('- ')

    if line.strip() == '':
        LOG.info('Line %d - Ignoring blank line' % i)
        continue

    # Comment
    if line.startswith('#'):
        LOG.info('Line %d - Ignoring commented-out line "%s"' % (i, lineclean))
        continue

    # Project
    if not line.startswith('-'):
        # This is a project, so start fresh (clear any items)
        project_id = find_project_by_name(lineclean, projects)
        if not project_id:
            LOG.error('Line %d - Invalid project name, cannot create subitems of "%s"' % (i, lineclean))
            error_count += 1
        else:
            LOG.info('Line %d - Loaded project "%s"' % (i, lineclean))
        milestone_id = 0
        milestones = dict()
        task_id = 0
        tasks = dict()
        subtask_id = 0
        # We've dealt with the project line, so move to next line
        continue

    # Process any attributes for this line
    attributes = {}
    matches = re.findall(' [alpsvd]=[\d-]*', lineclean)
    if matches:
        for match in matches:
            # Separate the attribute key and its value
            key, val = match.split('=')

            if key == ' a':
                attributes['assignee_id'] = int(val)

            if key == ' l':
                attributes['label_id'] = int(val)

            if key == ' p':
                attributes['priority'] = val
                if int(attributes['priority']) < -2 or int(attributes['priority']) > 2:
                    attributes['priority'] = 0
                    LOG.warning(
                        'Line %d - Priority must be between -2 and 2. Setting priority of 0 for "%s"' % (i, lineclean))
                    warning_count += 1

            if key == ' s':
                try:
                    start_date = datetime.datetime.strptime(val, "%Y-%m-%d")
                    attributes['start_on'] = start_date.strftime('%Y-%m-%d')
                except Exception:
                    LOG.warning('Line %d - Wrong date format; could not set "start on" date for "%s"' % (i, lineclean))
                    warning_count += 1

            if key == ' d':
                try:
                    end_date = datetime.datetime.strptime(val, "%Y-%m-%d")
                    attributes['due_on'] = end_date.strftime('%Y-%m-%d')
                except Exception:
                    LOG.warning('Line %d - Wrong date format; could not set "due on" date for "%s"' % (i, lineclean))
                    warning_count += 1

            if key == ' v':
                attributes['visibility'] = val
                if int(attributes['visibility']) != 0 and int(attributes['visibility']) != 1:
                    attributes['visibility'] = 1
                    LOG.warning(
                        'Line %d - Visibility must be 0 (private) or 1 (public). Setting visibility of 1 for "%s"' % (i, lineclean))
                    warning_count += 1

            lineclean = lineclean.replace(match, '')

    # If we don't have a valid project, we can't add any subitems
    if not project_id:
        LOG.error('Line %d - Invalid project name, could not add "%s"' % (i, lineclean))
        error_count += 1
        continue

    # Milestone
    if re.match('^-[\w\d ]', line):
        milestone_name = lineclean
        # Get all milestones for the current project
        milestones = project_milestones(project_id)
        #See if a matching milestone exists
        milestone_id = find_milestone_by_name(milestone_name, milestones)

        if not milestone_id:
            # Create a new milestone and store its milestone_id for subitems (tasks)
            created_milestone = create_milestone(project_id, milestone_name, attributes)
            milestone_id = created_milestone['id']
            if created_milestone:
                LOG.info('Line %d - Milestone doesn\'t exist; created new milestone #%d "%s"' %
                         (i, milestone_id, milestone_name))
            else:
                LOG.error('Line %d - Milestone doesn\'t exist and could not create milestone "%s"' % (i, lineclean))
                error_count += 1
        else:
            LOG.info('Line %d - Loaded milestone "%s"' % (i, lineclean))

    # Task
    if re.match('^--[\w\d ]', line):
        task_name = lineclean
        # Get all tasks (open and closed, not archived) within the project
        tasks = project_tasks(project_id)
        #See if a matching task exists (strip off beginning - and space chars)
        task_id = find_task_by_name(milestone_id, task_name, tasks)

        if not task_id:
            # Create a new task and store its task_id for subtasks
            created_task = create_task(project_id, milestone_id, task_name, attributes)
            task_id = created_task['task_id']
            if created_task:
                LOG.info('Line %d - Task doesn\'t exist; created new task #%d "%s"' % (i, task_id, task_name))
            else:
                LOG.error('Line %d - Task doesn\'t exist and could not create task "%s"' % (i, lineclean))
                error_count += 1
        else:
            LOG.info('Line %d - Loaded task #%d "%s"' % (i, task_id, lineclean))

    # Subtask
    if re.match('^---[\w\d ]', line):
        if not task_id:
            LOG.error('Line %d - Could not create or lookup parent task, could not add "%s"' % (i, lineclean))
            error_count += 1
        else:
            subtask_name = lineclean
            # We don't support task editing, but we should prevent duplicates, so get all subtasks
            subtasks = task_subtasks(project_id, task_id)
            #See if a matching subtask exists (strip off beginning - and space chars)
            subtask_id = find_subtask_by_name(subtask_name, subtasks)

            if subtask_id:
                LOG.error('Line %d - Subtask already exists, could not add "%s"' % (i, lineclean))
                error_count += 1
            else:
                # Create a new subtask under the current project_id/task_id
                if create_subtask(project_id, task_id, subtask_name, attributes):
                    LOG.info('Line %d - Created subtask "%s"' % (i, subtask_name))

LOG.info('Finished processing import file.')
if error_count > 0 or warning_count > 0:
    LOG.info('%d errors detected. Please view the log above.' % error_count)
    LOG.info('%d warnings detected. Please view the log above.' % warning_count)
else:
    LOG.info('No errors or warnings detected.')
