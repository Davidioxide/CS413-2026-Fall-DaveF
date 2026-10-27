AI tool: GPT 5.6 luna-medium
# Prompts:

- "Go to assigns/06, and read the MySolution/spec.md. Follow the instructions inside to implement what is specified inside."
- "the import of lambda1_vp" is not successful at compile time in some files, like demo.py. Please resolve its path for all files if they also imported lambda1_vp. Again, it is a file from assigns/05.
- "Make sure that we are building the correct app, as now we have demo.py, but we really wanted an app that onces called, has a CLI that we can interact with, and type our source language, which will be responded with target language"
- "The parser can fail on inputs. For example, an input of D0Evar("x") when running app.py can return PARSER ERROR: unexpected input near '"x")', and D0Elam("x", D0Evar("x")) returns PARSER ERROR: unexpected input near '"x", D0Evar("x"))'. Whereas the expected behavior is input D0Evar("x") returns x, and input D0Elam("x", D0Evar("x")) returns (lam x. x). Verify that this is a parser error and fix it. If it is not a parser error, find the real problem and fix it."
- "First, study app.py and understand how it uses CLI to interact with the user. Then, under tests/, create a file of test_app.py, which uses app.py as a CLI app and test at least with 100 inputs, to make sure that all of the tests fits the requirements under `Assign06.md`, and `REQUIREMENTS.md`, if any tests failed, fix them."
- "read through spec.md, Assign06.md, and REQUIREMENTS.md. It is clear that the current app.py only reduces input to church-encoded lambda calculus. Now, implement the functionality of asking user if they want to "observe" the value by pressing y or n. On the other hand, update all existing tests such that they don't only produce the correct lambda terms but can also be observed into primitive results, for example, TRUE = lam t. lam f. t = true. TRUE is the first input, and the lambda term is the first output, when program asks if user wants to observe the value, if yes, then true is the output. Make sure that all tests pass, and add more tests to fulfilled the requirements specified in the md files mentioned"
- "currently the program has a bug when observing the value, which causes an observation error. For example: NUM (2) returns (NUM (lam s. (lam z. (s (s z))))), but when choosing to observe the value, it raises OBSERVATION ERROR: could not infer the result kind. Please fix it, and make sure that everything in the tests/ also pass the comprehensive tests set"

# Revisions:

- With the help from agent, fixed a parser issue. 
- The app only reduces to church-encoded lambda calculus, but not primitive values

# How I reviewed and tested the code:

- In addition to the tests, I also asked AI to build on top an interactive CLI app which uses the existing implementations and return target language upon the valid input. 
