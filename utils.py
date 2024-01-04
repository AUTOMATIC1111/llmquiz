import dataclasses
import json
import os


@dataclasses.dataclass
class PromptTemplate:
    name: str
    system: str
    system_start: str
    system_end: str
    user_start: str
    user_end: str
    assistant_start: str
    assistant_end: str
    modelnames: list = None
    priority: int = 0


prompt_templates: list[PromptTemplate] = []


def load_templates(dirname):
    s = []

    for filename in os.listdir(dirname):
        with open(dirname + "/" + filename, "r", encoding="utf8") as file:
            jsdata = json.load(file)

        template = PromptTemplate(**jsdata)
        s.append(template)

    s = sorted(s, key=lambda x: x.priority, reverse=True)

    prompt_templates.clear()
    prompt_templates.extend(s)


def find_prompt_template(modelname):
    target = modelname.lower()

    for x in prompt_templates:
        for name in x.modelnames or []:
            if name.lower() in target:
                return x

    return prompt_templates[-1]


