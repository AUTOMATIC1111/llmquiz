# About
This is the code I use to quiz large language models. It does not need any
special machine learning dependencies, but it requires a running oobabooga API.

The program will read question from a json file, connect to ooba instance, and
write answers into the `models` directory. I have included an
example [questions.json](questions.json) file that demonstrates the format.

Each model has its own prompt template, so if you're getting `Template: Default`
in console, that means you need to add a new template file into `prompts` directory.
