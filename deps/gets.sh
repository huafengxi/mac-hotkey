#!/usr/bin/env osascript
try
    set dialogResult to display dialog "input tag" default answer ""
on error number -128
    set dialogResult to {button returned: "OK", text returned: ""}
end try

if button returned of dialogResult is "OK" then
    return text returned of dialogResult
else
    return ""
end if
