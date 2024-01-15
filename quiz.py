"""
This script connects to a running ooba instance on port 5000 and quizzes it on questions from questions.json file.
"""

import dataclasses
import os.path

import requests
import json
import utils
import tqdm

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--questions', help='json file with questions', default='questions.json')
parser.add_argument('--outdir', help='output directory', default='models')
parser.add_argument('--api', help='API URL for ooba text ui', default='http://127.0.0.1:5000')
parser.add_argument('--promptdir', help='directory with prompt templates for different models', default='prompts')
parser.add_argument('--template', help='force prompt format with specified name')
parser.add_argument('--sysprompt', help='use custom system prompt from file')
args = parser.parse_args()

question_letters = ['M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', ]


with open(args.questions, "r", encoding="utf8") as file:
    question_db = json.load(file)

db = question_db["questions"]


utils.load_templates(args.promptdir)


def request(prompt, extra=None, path='v1/completions'):
    url = f"{args.api}/{path}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "mode": "instruct",
        "max_tokens": 0,
        "prompt": prompt,
    }

    data.update(extra)

    response = requests.post(url, headers=headers, json=data, verify=False)

    return response.json()


def setup_prompt(q, a=None):
    res = ''

    if system_prompt is not None:
        res += prompt_template.system_start
        res += system_prompt
        res += prompt_template.system_end

    res += prompt_template.user_start
    res += q
    res += prompt_template.user_end

    res += prompt_template.assistant_start
    if a is not None:
        res += a

    return res


@dataclasses.dataclass
class QuizAnswer:
    model: str = None
    prompt: str = None
    letter: str = None
    index: int = None
    probs: dict = None
    question: str = None
    answer: str = None
    created: int = None
    total_prob: float = None


def quiz(question, letters, answer_start=None):
    letter_indexes = {l: i for i, l in enumerate(letters)}
    probs_all = request(setup_prompt(question, a=answer_start), {"top_logits": 100, "use_samplers": False}, path='v1/internal/logits')
    total_all = sum(v for k, v in probs_all.items())
    probs = {x: probs_all.get(x, 0) for x in letters}
    total = sum(v for k, v in probs.items())
    probs = {k: round(v/total * 100, 2) for k, v in probs.items()}

    probs_sorted = dict(sorted(probs.items(), key=lambda x: -x[1]))
    top_answer, top_prob = next(iter(probs_sorted.items()))

    prob_ratio = total / total_all
    if prob_ratio < 0.25:
        print("WARNING")
        print(f"  total probability of letters is too low: {prob_ratio}; top choices: {probs_all}")

        ea = request(setup_prompt(question, a=answer_start), {"max_tokens": 200, "temperature": 0.001})
        ea = ea['choices'][0]["text"]
        print(f"  example answer: <<<{ea}>>>")

    answer = request(setup_prompt(question, a=top_answer), {"max_tokens": 200, "temperature": 0.001})
    answer_text = answer['choices'][0]["text"]

    return QuizAnswer(
        model=answer["model"],
        prompt=setup_prompt('QUESTION', a='ANSWER'),
        letter=top_answer,
        index=letter_indexes[top_answer],
        probs={letter_indexes[k]: v for k, v in probs.items()},
        question=question,
        answer=f"{top_answer}{answer_text}",
        created=answer["created"],
        total_prob=prob_ratio,
    )


dummy = request('hello', {"logprobs": 2, "temperature": 0.001, "max_tokens": 2})
model = dummy["model"]
print(f"Model: {model}")

prompt_template = utils.find_prompt_template(model, force=args.template)
system_prompt = prompt_template.system
print(f"Template: {prompt_template.name}")

if args.sysprompt:
    with open(args.sysprompt, encoding="utf8") as file:
        system_prompt = file.read()

os.makedirs(args.outdir, exist_ok=True)
path = os.path.join(args.outdir, f'{model}.json')
if os.path.exists(path):
    with open(path, 'r', encoding='utf8') as file:
        answers = json.load(file)
else:
    answers = {"answers": {}}


for q in tqdm.tqdm(db.values()):
    name = q["name"]
    text = q["question"]
    qanswers = q["answers"]

    if name in answers["answers"]:
        continue

    letters = question_letters[0:len(qanswers)]

    options = "\n".join(f"[{letter}]. {possible_answer['text']}" for letter, possible_answer in zip(letters, qanswers))

    answer_start = '\nAnswer: ['
    question = f"""{question_db.get('common_text', '')}{text}
Options:
{options}

Start with the letter and then explain why you made this choice.
"""

    answer = quiz(question.strip(), letters=letters, answer_start=answer_start)
    answers["answers"][name] = {
        "choice": answer.index,
        "probs": answer.probs,
        "total_prob": answer.total_prob,
        "question": answer.question,
        "answer": answer.answer,
        "created": answer.created,
    }

    def check_field(obj, fieldname, value):
        if fieldname not in obj:
            obj[fieldname] = value
        else:
            assert obj[fieldname] == value

    check_field(answers, "answer_start", answer_start)
    check_field(answers, "system_prompt", system_prompt)
    check_field(answers, "template_name", prompt_template.name)
    check_field(answers, "system_prompt", system_prompt)
    check_field(answers, "model", answer.model)
    check_field(answers, "prompt", answer.prompt)

    with open(path, "w", encoding="utf8") as file:
        json.dump(answers, file, indent=4, ensure_ascii=False)
