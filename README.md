EasyImport for Active Collab 3
=============

##Description

EasyImport for Active Collab 3 makes it easy to import milestones, tasks, and subtasks into Active Collab projects.

##Features

- Only supports existing projects
- Does not modify existing objects (just adds sub-items)
- Looks up existing items by title. If title matches exactly, subitems will be added to the existing item.
- Prevents duplicate milestones at the project-level
- Prevents duplicate tasks at the milestone-level, if milestone supplied (supports same-named task under multiple milestones)
- Prevents duplicate subtasks at the task-level
- Set label, priority, start on date, due on date, and assignee independently on each item (see *Future plans*)

##Usage

###Setup
This script requires a configuration file. The script will automatically create this for you the first time you run the script with a valid import file (see *How to use the script*). Here's an example of the output:

> [ WARN  ]   No config file found. Created a blank config file. Please edit /Users/adam/.aceasyimportconfig and try again.

You must open this new file and add an API url (your Active Collab url) and an API token (find this in your Active Collab user profile).

###How to use the script
Please run the script with `-h` to show how to use the script.
> `python easyimport.py -h`

The script only requires one argument, which is the path to an import file (explained below).
> `python easyimport.py myimportfile.txt`

##Import Files
This script is called EasyImport for a reason! It's meant to be a very simple way to import milestones, tasks, and subtasks.

* Each separate project, milestone, task, or subtask must be on its own line
* Milestones and tasks must have a parent project line (see *Import file example*)
* How you begin the line determines what type of item you're importing (see *Character Table*)
* Each line may accept various attributes like *Assignee ID* and *Priority* (see *Attributes and values*)
* When a milestone line is read, all tasks following, until the next milestone or project line is read, will be added under that milestone. So, if you want to add tasks that are not under a milestone, add them just after the project title line, before any milestone lines.
* Though it's discouraged, you may include a space after the opening characters if you'd like (shown in "Paint" example below)

###Character Table

| Begin line with                             | type        | handling                      |
| --------------------------------------------| ----------- | ----------------------------  |
| `#`                                         | Comment     | ignore line                   |
| First character is anything but `#` and `-` | Project     | title lookup only  (required) |
| `-`                                         | Milestone   | lookup, create if not found   |
| `--`                                        | Task        | lookup, create if not found   |
| `---`                                       | Subtask     | create only                   |

###Attributes and values

- Set assignee ID with: a=n (n = user id)
- Set label ID with: l=n (n = label id)
- Set priority with: p=n (n = -2, -1, 0, 1, or 2; 2 is "Highest", -2 is "Lowest")
- Set visibility with: v=n (n = 0 or 1; 0 is "private", 1 is "public")
    - if omitted, visibility will be 1 (public)
- Set "start on" date with: s=YYYY-MM-DD
    - for milestones this defaults to *today* because it's required
- Set "due on" date with: d=YYYY-MM-DD
    - for milestones this defaults to *1 year from today* because it's required

Note: only one date format is currently accepted: *YYYY-MM-DD*

## Import file example

![Example.txt](ftplugin_demo.png?raw=true)

##Vim syntax highlighting and folding

Do you notice the pretty colors and folding in the example screenshot above? You can get those too!

If you edit your import files in Vim, I **strongly** encourage you to install the file type plugins I've made for the aceasyimport file type. You're probably saying, "I didn't realize there was a specific file type." Well, there isn't, really. I suggest saving your import files as *.txt* files.

You'll find the plugin in the *vim* directory of the aceasyimport repo. You can either copy the files to the correct directories, or you can create symlinks (so that you can still git-pull any changes I make in the future).

###Setup
You should make the files accessible at the following locations:

	~/.vim/ftplugin/aceasyimport.vim
	~/.vim/syntax/aceasyimport.vim

###Usage
You can either run `set ft=aceasyimport` every time you open an import file, or simply add the following modeline to the top of your import scripts. The latter automatically enables the proper syntax highlighting and code folding I'm providing through the ftplugin:

	# vim: set ft=aceasyimport :

##Future plans
- Support more properties (e.g., other/secondary assignees)
