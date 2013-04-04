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

###Character Table

| Begin line with                             | type        | handling                      |
| --------------------------------------------| ----------- | ----------------------------  |
| `#`                                         | Comment     | ignore line                   |
| First character is anything but `#` and `-` | Project     | title lookup only  (required) |
| `-`                                         | Milestone   | lookup, create if not found   |
| `--`                                        | Task        | lookup, create if not found   |
| `---`                                       | Subtask     | create only                   |

###Attributes and values

- Set assignee ID with: a=*n* (n = user id)
- Set label ID with: l=*n* (n = label id)
- Set priority with: p=*n* (n = -2, -1, 0, 1, or 2; 2 is "Highest" -2 is "Lowest")
- Set "start on" date with: s=YYYY-MM-DD
    - for milestones this defaults to *today* because it's required
- Set "due on" date with: d=YYYY-MM-DD
    - for milestones this defaults to *1 year from today* because it's required

Note: only one date format is currently accepted: *YYYY-MM-DD*

###Tips

* When a milestone line is read, all tasks following, until the next milestone or project line is read, will be added under that milestone. So, if you want to add tasks that are not under a milestone, add them just after the project title line, before any milestone lines.
* Though it's discouraged, you may include a space after the opening characters if you'd like (shown in "Paint" example below)

## Import file example

	# Import File Demo
	Sell the house
	--Do pricing research
	--Find real estate agent p=2
	-Clean s=2013-10-02 d=2013-10-29
	--Clean attic a=5 l=6
	---Throw away as much as possible p=2
	---Donate clothes to Goodwill p=1
	--Clean basement
	--Clean shed
	- Paint
	-- Paint the upstairs bedrooms
	--- Master bedroom
	--- Kids bedroom

##Future plans
- Allow and ignore blank lines
- Support more properties (e.g., other/secondary assignees)
