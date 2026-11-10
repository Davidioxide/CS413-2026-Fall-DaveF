# Main prompts
- "Read spec.md, Assign07.md, and README.md, and follow the instructions inside to build the program specified."
- "Expand each test suite, and separate these tests suites into different .py files."
- "Create a Makefile that facilitates testing, and record the ways to use the make commands in `README.md`."
- "Switch to FAST API in implementing the service"

# Testing

The testing is mainly done by calling make commands to test four test suites under /MySolution/tests. Upon testing, it turns out that the AI model defaults to python's http service instead of using FAST API, it is now fixed and replaced by FAST API.