syn match aceasyimportComment   "^#.*$"
syn match aceasyimportTodo      "^# \=TODO.*$"

" These must go in this order so the last match overrides an earlier match
syn match aceasyimportProject   "^[A-Za-z0-9].*$"
syn match aceasyimportMilestone "^- \=.*$"
syn match aceasyimportTask      "^-- \=.*$"
syn match aceasyimportSubtask   "^--- \=.*$"

" These use arbitrary syntax group names (e.g., Conditional; :help group-name) 
" I did choose from the 'preferred' groups
hi def link aceasyimportTodo       Todo
hi def link aceasyimportComment    Comment
hi def link aceasyimportProject    Underlined
hi def link aceasyimportMilestone  Identifier
hi def link aceasyimportTask       Constant
hi def link aceasyimportSubtask    Statement

let b:current_syntax = "aceasyimport"
