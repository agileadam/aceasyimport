function! NextNonBlankLine(lnum)
    let numlines = line('$')
    let current = a:lnum + 1

    while current <= numlines
        if getline(current) =~? '\v\S'
            return current
        endif

        let current += 1
    endwhile

    return -2
endfunction

function! PrevNonBlankLine(lnum)
    let current = a:lnum - 1

    while current > 0
        if getline(current) =~? '\v\S'
            return current
        endif

        let current -= 1
    endwhile

    return -2
endfunction

function! BelongsToMilestone(lnum)
    let current = a:lnum - 1

    while current > 0
        if getline(current) =~ '^[A-Za-z0-9]'
			" We only want to check for a milestone within the current project
			" Because we hit another project before finding a milestone, we exit
            return -2
        endif

        if getline(current) =~ '^- \=[A-Za-z0-9]'
			" vimscript doens't have booleans, so we might as well return the line number
            return current
        endif

        let current -= 1
    endwhile

    return -2
endfunction

function! AcEasyImportFolds()
	let thisline = getline(v:lnum)
	let nextline = getline(NextNonBlankLine(v:lnum))
	let prevline = getline(PrevNonBlankLine(v:lnum))

	" We'll use this to determine what foldlevel to set for tasks
	let belongstomilestone = BelongsToMilestone(v:lnum)

	if thisline =~? '\v^\s*$'
		return '-1'
	elseif thisline =~ '^--- \=[A-Za-z0-9]'
		return '='
	elseif thisline =~ '^-- \=[A-Za-z0-9]'
		if nextline =~ '^--- \=[A-Za-z0-9]'
			" Has subtask(s)
			if belongstomilestone > 0
				return '>3'
			else
				return '>2'
			endif
		else
			" No subtask(s)
			if belongstomilestone > 0
				return '2'
			else
				return '1'
			endif
		endif
	elseif thisline =~ '^- \=[A-Za-z0-9]'
		if nextline =~ '^-- \=[A-Za-z0-9]'
			return '>2'
		else
			return '1'
		endif
	elseif thisline =~ '^[A-Za-z0-9]'
		return '>1'
	else
		return '-1'
	endif
endfunction

setlocal foldcolumn=4
setlocal foldmethod=expr
setlocal foldexpr=AcEasyImportFolds()
 
function! AcEasyImportFoldText()
	let foldsize = (v:foldend-v:foldstart)
	return getline(v:foldstart).' ('.foldsize.' lines)'
endfunction

setlocal foldtext=AcEasyImportFoldText()
