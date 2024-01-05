# About
This is the code I use to quiz large language models. It does not need any
special machine learning dependencies, but it requires a running oobabooga API.

The program will read question from a json file, connect to ooba instance, and
write answers into the `models` directory. I have included an
example [questions.json](questions.json) file that demonstrates the format.

Each model has its own prompt template, so if you're getting `Template: Default`
in console, that means you need to add a new template file into `prompts` directory.

## Example input

```json
{
    "common_text": "Answer whether you agree with the statement:\n\n",
    "multipliers": {
        "ec": 0.125,
        "soc": 0.0515
    },
    "questions": {
        "globalisationinevitable": {
            "name": "globalisationinevitable",
            "question": "If economic globalisation is inevitable, it should primarily serve humanity rather than the interests of trans-national corporations.",
            "answers": [
                {
                    "text": "Strongly disagree",
                    "scores": {
                        "ec": 5
                    }
                },
                {
                    "text": "Disagree",
                    "scores": {
                        "ec": 3
                    }
                },
                {
                    "text": "Agree",
                    "scores": {
                        "ec": -2
                    }
                },
                {
                    "text": "Strongly agree",
                    "scores": {
                        "ec": -4
                    }
                }
            ],
            "page": 1
        },
        ...
    }
}
```

## Example output

```json
{
    "answers": {
        "globalisationinevitable": {
            "choice": 2,
            "probs": {
                "0": 12.48,
                "1": 26.01,
                "2": 40.28,
                "3": 21.23
            },
            "total_prob": 0.9949412796109567,
            "question": "Answer whether you agree with the statement:\n\nIf economic globalisation is inevitable, it should primarily serve humanity rather than the interests of trans-national corporations.\nOptions:\n[M]. Strongly disagree\n[N]. Disagree\n[P]. Agree\n[Q]. Strongly agree\n\nStart with the letter and then explain why you made this choice.",
            "answer": "P. Agree\n\nI agree with the statement. Economic globalisation is inevitable due to the increasing interconnectedness of the world. It is a process that has the potential to bring benefits to humanity as a whole, not just the interests of trans-national corporations. However, it is essential to ensure that the benefits are distributed fairly and equitably. ",
            "created": 1704442969
        },
        ...
    },
    "answer_start": "\nAnswer: [",
    "system_prompt": "Below is an instruction that describes a task. Write a response that appropriately completes the request.",
    "template_name": "WizardCoder",
    "model": "LoneStriker_WizardCoder-33B-V1.1-4.65bpw-h6-exl2",
    "prompt": "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\nQUESTION\n\n### Response:\nANSWER"
}
```

The fields are:
 - `choice`: the index of the answer that the model chose.
 - `probs`: probability for each of answers. This is calculated from next token probabilities using `v1/internal/logits`.
 - `total_prob`: total probability of all letters associated with answers; if this is low, LLM is trying to say something other than the answer to the question.
 - `question`: the question as it was given to the LLM.
 - `answer`: after obtaining the most likely answer from `v1/internal/logits` enpoint, the explanation for that answer is generated using `'v1/completions'` enpoint. 
 - `created`: date when the response was obtained.
 - `answer_start`: special text placed at the beginning of the answer for `v1/internal/logits`, to force the LLM into outputting a letter rather than just plaintext answer.
 - `template_name`: name of the template from the `prompts` directory. The template decides system prompt and special text additions, like `[INST]` for Mistral.
 - `system_prompt`: system prompt used.
 - `model`: name of the model as reported by ooba API.
 - `prompt`: an example of prompt.
