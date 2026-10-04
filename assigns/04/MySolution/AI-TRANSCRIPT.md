# AI Transcript

AI Tool used: GPT-5.6-Luna medium

## Prompts:

1. "Read `MySolution/spec.md` first, then read `Assing04.md`, and execute the errands specified inside. Notice that `lambda1.py` is a provided source file mentioned in `spec.md`"
2. "Run the tests inside /MySolution/tests" and make sure that all the assertion passed, if any of the assertion fails, write in a separate `MySolution/tests/bugs.md` to reveal the bugs".
3. "Run the program now using the commands specified in TESTING.md, make sure to close the server as the website is shut down"
4. "There's a bug in the webpage that when the webpage is initialized, `Load source` and `Choose file` are not clickable, until when the user pressed on `Discard changes` button, will `Load source` and `Choose file` button work, fix this and record the bug, reason of the bug, and how it is fixed inside `MySolution/tests/log_bugs.md` "
5. "Format `MySolution/source/index.html` and `MySolution/source/style.css`", apply more round-square design to the webpage, and decorate it using black and cyan color".
6. "In the webpage, the `<h1>` or `<span>` tag of page-header is clearly not occupying the whole space, thus the title 'LAMBDA Web Front-End' is forced to wrap around, fix this by allocating either relative width or more width, and choose the option that makes more sense"

## Manual edits

- I inspected the page and found the error that "Load source" and "Choose File" buttons can't work after initialization, and fixed it with the help of AI. 
- I insepcted the source code of HTML/CSS and found bad design. Under close inspection, it is because `<h1>` tag is limited to `max-width:14ch`, and told AI to fix it using reasonable approach.