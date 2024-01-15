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
    templates = {}

    for filename in os.listdir(dirname):
        with open(dirname + "/" + filename, "r", encoding="utf8") as file:
            jsdata = json.load(file)

        templates[jsdata["name"]] = jsdata

    res = []

    for jsdata in templates.values():
        copyfrom = jsdata.pop('copyfrom', None)
        src = None
        if copyfrom is not None:
            src = templates[copyfrom]
            for k, v in src.items():
                if k not in jsdata:
                    jsdata[k] = v

        template = PromptTemplate(**jsdata)

        if src is not None:
            template.priority = src.get('priority', 0) + 10

        res.append(template)

    res = sorted(res, key=lambda x: x.priority, reverse=True)

    prompt_templates.clear()
    prompt_templates.extend(res)


def find_prompt_template(modelname, force=None):
    target = modelname.lower()

    if force:
        for x in prompt_templates:
            if x.name == force:
                return x

        raise Exception(f"Couldn't find prompt template named {force}")

    for x in prompt_templates:
        for name in x.modelnames or []:
            if name.lower() in target:
                return x

    return prompt_templates[-1]


