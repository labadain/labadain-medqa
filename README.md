![Labadain-MedQA overview](Labadain-MedQA-Tetun.png)

# Overview

Labadain-MedQA is a collection of datasets, models, and evaluation resources for medical question answering (QA) in Tetun, a low-resource language spoken in Timor-Leste. It comprises English–Tetun medical QA datasets, QLoRA fine-tuned language models, translation-quality evaluation resources, and translated USMLE evaluation sets.

The resources support:

- Fine-tuning language models for Tetun medical QA.
- Evaluating English-to-Tetun medical translation quality.
- Evaluating model performance on translated medical multiple-choice questions.
- Research on cross-lingual medical knowledge transfer and information access in Tetun.

This repository provides the prompts and supporting reference files used in the construction and evaluation of Labadain-MedQA. The published datasets and models are available under the [`labadain` account on Hugging Face](https://huggingface.co/labadain).

# Resource Description

| Resource | Contents |
| --- | --- |
| Training datasets | 39,077 English–Tetun medical QA pairs from two datasets |
| Fine-tuned models | Six QLoRA/PEFT adapters from the Gemma 4 and Llama 3 families |
| Translation evaluation | 100 medical QA documents and human assessment scores |
| Downstream evaluation | 325 translated USMLE multiple-choice questions across three collections |
| Translation, construction, and evaluation materials | Reusable translation pipeline; and translation, orthographic rules, vocabulary references, and evaluation prompts |


# Datasets

## Medical QA Training Data

The translated MedAlpaca datasets contain 39,077 English–Tetun medical QA pairs, of which only the Tetun questions and answers were used for model fine-tuning.

- [Medical Flashcards](https://huggingface.co/datasets/labadain/Labadain-MedQA-MedAlpaca-Medical-Flashcards-English-Tetun): 33,135 QA pairs covering biomedical and clinical knowledge.
- [WikiDoc Patient Information](https://huggingface.co/datasets/labadain/Labadain-MedQA-MedAlpaca-WikiDoc-Patient-Information-English-Tetun): 5,942 QA pairs covering medical conditions, symptoms, treatments, and patient information.

## Data Structure

Each QA pair contains four fields:

| Field | Description |
| --- | --- |
| `input_en` | Question in English |
| `input_tdt` | Question in Tetun |
| `output_en` | Answer in English |
| `output_tdt` | Answer in Tetun |

The Tetun fields support instruction fine-tuning, while the parallel English–Tetun data are intended to support future research on cross-lingual medical QA and translation.

Example record (Medical Flashcards and WikiDoc Patient Information):

```json
{
  "input_en": "What is the relationship between very low Mg2+ levels, PTH levels, and Ca2+ levels?",
  "input_tdt": "Saida mak relasaun entre nível Mg2+ ne'ebé ki'ik tebes, nível PTH, no nível Ca2+?",
  "output_en": "Very low Mg2+ levels correspond to low PTH levels which in turn results in low Ca2+ levels.",
  "output_tdt": "Nível Mg2+ ne'ebé tun tebes korresponde ho nível PTH ne'ebé tun, ne'ebé ikus mai rezulta nível Ca2+ ne'ebé tun."
}
```

## Loading the Datasets

The datasets can be loaded using the Hugging Face `datasets` library:

```bash
pip install datasets
```

```python
from datasets import load_dataset

flashcards = load_dataset(
    "labadain/Labadain-MedQA-MedAlpaca-Medical-Flashcards-English-Tetun",
    split="train"
)

wikidoc = load_dataset(
    "labadain/Labadain-MedQA-MedAlpaca-WikiDoc-Patient-Information-English-Tetun",
    split="train"
)

print("Medical Flashcards:", len(flashcards))
print("WikiDoc Patient Information:", len(wikidoc))

# Display an English–Tetun QA pair from each dataset
print(flashcards[0])
print(wikidoc[0])
```

The Tetun question and answer fields were used to construct instruction–response examples for model fine-tuning. The training format depends on the selected model and its chat template.

# Evaluation Resources

The evaluation resources support translation quality assessment and downstream model evaluation.

### Translation Quality Evaluation

Translation quality was evaluated on 100 randomly selected medical QA documents (50 question-answer pairs), using human reference translations and assessments by two native Tetun-speaking healthcare professionals.

- [Translation Evaluation Sample](https://huggingface.co/datasets/labadain/Labadain-MedQA-Sample-for-Evaluation-English-Tetun): Contains English originals, human reference translations, and LLM-generated translations for 100 medical QA documents.
- [Human Translation Assessment Scores](https://huggingface.co/datasets/labadain/Labadain-MedQA-Human-Assessment-Scores-English-Tetun): Contains human evaluation scores for medical accuracy and Tetun fluency.

Example record from the **Translation Evaluation Sample**:

```json
{
  "english_text": "What is the association between mycophenolate mofetil use and blood pressure?",
  "translation_human": "Saida mak relasaun entre uzu mikofenolatu mofetila no tensaun arteriál (raan)?",
  "translation_llm": "Saida mak asosiasaun entre uza mikofenolatu mofetil no presaun raan?"
}
```

Example record from the **Human Translation Assessment Scores** dataset:

```json
{
  "TQ001": {
    "english_text": "What is the association between mycophenolate mofetil use and blood pressure?",
    "translation_a": "Saida mak relasaun entre uzu mikofenolatu mofetila no tensaun arteriál (raan)?",
    "translation_b": "Saida mak asosiasaun entre uza mikofenolatu mofetil no presaun raan?",
    "ratings": {
      "a1_a_medical_accuracy": 4,
      "a1_a_tetun_fluency": 4,
      "a1_b_medical_accuracy": 4,
      "a1_b_tetun_fluency": 4,
      "a2_a_medical_accuracy": 5,
      "a2_a_tetun_fluency": 5,
      "a2_b_medical_accuracy": 5,
      "a2_b_tetun_fluency": 5
    }
  }
}
```

The human-assessment rating fields use the pattern
`<annotator>_<system>_<criterion>`:

| Component | Meaning |
| --- | --- |
| `a1` or `a2` | Annotator 1 or annotator 2 |
| `a` or `b` | Translation system A or translation system B |
| `medical_accuracy` | Score for medical accuracy |
| `tetun_fluency` | Score for Tetun fluency |

System A is the human translation, and system B is the LLM-generated translation. For example, `a1_a_medical_accuracy` is annotator 1's medical-accuracy score for the human translation, while `a1_a_tetun_fluency` is annotator 1's Tetun-fluency score for the human translation. Fields with `_b_` refer to the LLM-generated translation; the `a2_` fields contain the corresponding scores from annotator 2.

The human assessment was conducted using the annotation system shown below.

![Translation quality annotation system](translation_quality_assessment_tool.png)


### Evaluation on Medical QA Datasets

Three English–Tetun USMLE datasets provide 325 multiple-choice questions for evaluating language models on medical knowledge and reasoning tasks in Tetun.

| Dataset | Questions | Coverage |
| --- | ---: | --- |
| [USMLE Step 1](https://huggingface.co/datasets/labadain/Labadain-MedQA-USMLE-Step-1-English-Tetun) | 94 | Foundational medical sciences |
| [USMLE Step 2](https://huggingface.co/datasets/labadain/Labadain-MedQA-USMLE-Step-2-English-Tetun) | 109 | Clinical knowledge and its application |
| [USMLE Step 3](https://huggingface.co/datasets/labadain/Labadain-MedQA-USMLE-Step-3-English-Tetun) | 122 | Clinical decision-making and patient management |
| **Total** | **325** | |

Each dataset contains English and Tetun questions, answer options, and corresponding correct answers.

Each USMLE dataset uses the same record structure. The following abbreviated example applies to the records in Step 1, Step 2, and Step 3:

```json
{
  "question": "Serum LDL-cholesterol concentrations are measured in blood samples...",
  "question_tdt": "Konsentrasaun LDL-kolesterol iha serum sukat husi amostra raan...",
  "options": {
    "A": "105-155",
    "B": "120-140",
    "C": "125-135",
    "D": "128-132",
    "E": "129-131"
  },
  "options_tdt": [
    "{'A': '105-155', 'B': '120-140', 'C': '125-135', 'D': '128-132', 'E': '129-131'}"
  ],
  "answer": "120-140",
  "answer_tdt": "120-140",
  "answer_idx": "B"
}
```

The same fields are provided in the [USMLE Step 1](https://huggingface.co/datasets/labadain/Labadain-MedQA-USMLE-Step-1-English-Tetun), [USMLE Step 2](https://huggingface.co/datasets/labadain/Labadain-MedQA-USMLE-Step-2-English-Tetun), and [USMLE Step 3](https://huggingface.co/datasets/labadain/Labadain-MedQA-USMLE-Step-3-English-Tetun) datasets.

The datasets support accuracy-based evaluation using a multiple-choice prompt that instructs models to select one answer option. The evaluation prompt is available in the [Prompts and Reference Files](#prompts-and-reference-files) section.

These datasets are intended for evaluation rather than model fine-tuning, regardless of the split names used by the Hugging Face dataset viewer.

See all [Labadain-MedQA datasets](https://huggingface.co/labadain/datasets?search=MedQA).


## Models

Six instruction-tuned models from the Gemma 4 and Llama 3 families were adapted for Tetun medical QA using QLoRA on the translated MedAlpaca training datasets.

The published models are **PEFT adapters**, not standalone copies of the base models. Each adapter must be loaded with its compatible base model, as documented in the respective Hugging Face model card.

### Gemma 4

| Model | USMLE Macro-Average Accuracy |
| --- | ---: |
| [Gemma 4 12B QLoRA](https://huggingface.co/labadain/Labadain-MedQA-QLoRA-Gemma-4-12B-it-Tetun) | 48.64% |
| [Gemma 4 E4B QLoRA](https://huggingface.co/labadain/Labadain-MedQA-QLoRA-Gemma-4-E4B-it-Tetun) | 45.95% |
| [Gemma 4 E2B QLoRA](https://huggingface.co/labadain/Labadain-MedQA-QLoRA-Gemma-4-E2B-it-Tetun) | 26.25% |

### Llama 3

| Model | USMLE Macro-Average Accuracy |
| --- | ---: |
| [Llama 3.1 8B QLoRA](https://huggingface.co/labadain/Labadain-MedQA-QLoRA-LLaMA-3.1-8B-it-Tetun) | 21.75% |
| [Llama 3.2 3B QLoRA](https://huggingface.co/labadain/Labadain-MedQA-QLoRA-LLaMA-3.2-3B-it-Tetun) | 20.41% |
| [Llama 3.2 1B QLoRA](https://huggingface.co/labadain/Labadain-MedQA-QLoRA-LLaMA-3.2-1B-it-Tetun) | 17.61% |

The reported results correspond to the QLoRA evaluation configurations documented in the model cards, including the 4-bit inference configuration for the Gemma models. Macro-average accuracy is calculated as the unweighted mean of the accuracies across the three USMLE evaluation sets. Results for alternative precision or adapter-merging configurations may differ.

Each model card provides additional information about its base checkpoint, fine-tuning approach, evaluation results, and model-loading instructions.

See all [Labadain-MedQA models](https://huggingface.co/labadain/models?search=MedQA).

### Model Usage

The following example shows how to load and use the Gemma 4 E2B adapter. The LLaMA 3 adapters use similar settings: 4-bit loading, text-only generation, the same user-prompt format, and deterministic decoding (`do_sample=False`). Only the compatible base model and adapter identifiers change.

Install the inference dependencies:

```bash
pip install unsloth peft transformers torch bitsandbytes
```

```python
from peft import PeftModel
from unsloth import FastModel
import torch

base_model, tokenizer = FastModel.from_pretrained(
    model_name="unsloth/gemma-4-E2B-it",
    max_seq_length=2048,
    load_in_4bit=True,
)

model = PeftModel.from_pretrained(
    base_model,
    "labadain/Labadain-MedQA-QLoRA-Gemma-4-E2B-it-Tetun",
)
model.eval()

messages = [{"role": "user", "content": "Saida mak diabetes?"}]
inputs = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True,
).to(model.device)

with torch.inference_mode():
    output = model.generate(
        **inputs,
        do_sample=False,
        max_new_tokens=256,
    )

print(tokenizer.decode(output[0], skip_special_tokens=True))
```


## Resource Construction

The medical QA training datasets were derived from the MedAlpaca Medical Flashcards and WikiDoc Patient Information collections. The English source content was translated into Tetun using Gemini 2.5 Flash through a two-stage process:

1. **English-to-Tetun translation:** Medical QA content was translated using a prompt containing English–Tetun examples.
2. **Tetun orthographic revision:** The translated text was revised using a separate prompt guided by official Instituto Nacional de Linguística (INL) orthography, Portuguese-to-Tetun spelling adaptation rules, and curated vocabulary.

Both prompts were iteratively refined during development. The final prompts and supporting reference files are available in the [Prompts and Reference Files](#prompts-and-reference-files) section.

Translation quality was evaluated using human reference translations, automatic translation metrics, and assessments by two native Tetun-speaking healthcare professionals.


## Translation Pipeline

The reusable translation pipeline is provided in [`translation_pipeline/`](translation_pipeline/). It translates English medical QA text into Tetun and then applies a separate Tetun orthographic revision step before saving the output.

### Translation folder

```text
translation_pipeline/
├── prompts/
│   ├── en-tdt-translation-prompt.md
│   └── tetun-revision-prompt.md
├── src/
│   └── utils.py
├── .env.example
├── requirements.txt
└── translate.py
```

The `src/` directory contains the runtime support modules imported by `translate.py`. It must remain alongside `translate.py` when the pipeline is copied or published.

### Setup

Run the following commands from the `translation_pipeline/` directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `GEMINI_API_KEY` in `.env` before running the pipeline. The key is used to call Gemini for both English-to-Tetun translation and Tetun orthographic revision.

### Running translation

The dataset name is required. The range uses Python's half-open convention: `--init-range` is inclusive and `--end-range` is exclusive.

```bash
python translate.py \
  --dataset-name medalpaca/medical_meadow_wikidoc_patient_information \
  --init-range 0 \
  --end-range 10 \
  --output-dir translated_docs \
  --output-filename translated_docs.json
```

The first run downloads the Hugging Face dataset and stores it under `translation_pipeline/HF_dataset_to_translate/`. Later runs reuse the local dataset copy instead of downloading it again.

The output JSON contains the original English fields and the revised Tetun fields: `input`, `input_tdt`, `output`, and `output_tdt`. The translation and revision steps are completed before a record is written.

When LangSmith tracing is enabled, each input or output field appears under a `translation_revision` trace. It contains two child traces: `translation_result` and `revision_result`. Each child trace contains the complete constructed prompt and generated response under the record-level parent trace.

### Checkpoints and resuming

After each dataset row, the pipeline writes the translated output and updates a checkpoint file at:

```text
translated_docs/translated_docs_checkpoint.json
```

The checkpoint stores the dataset configuration and the next source index. If a translation request fails, rerun the same command to resume from the recorded index. The existing output JSON supplies the records already completed.


## Prompts and Reference Files

The following prompts and supporting reference files document the resource construction and evaluation pipeline.

### Translation and Orthographic Revision

- [English-to-Tetun translation prompt](translation_pipeline/prompts/en-tdt-translation-prompt.md): Instructions for translating English text into Tetun while preserving meaning, structure, formatting, names, and measurements.
- [Tetun orthographic revision prompt](translation_pipeline/prompts/tetun-revision-prompt.md): Instructions for revising Tetun text according to official Tetun orthography, Portuguese loanword adaptation rules, and curated vocabulary.

### Evaluation

Evaluation-specific prompts and resources are organized in [`evaluation/`](evaluation/).

- [Multiple-choice question evaluation prompt](evaluation/prompts/multiple-selection-prompt.md): Instructions for selecting the most appropriate answer to a medical multiple-choice question and returning one option label.

Additional [annotation tools and guidelines](annotation-tools-and-guidelines/) are provided in this repository.

## Intended Use and Limitations

Labadain-MedQA is intended for research on Tetun medical QA, medical information access, cross-lingual knowledge transfer, and the evaluation of language models in low-resource settings.

Users should consider the following limitations:

- The training datasets were generated through automatic translation and may contain medical, linguistic, or orthographic errors.
- Translation quality was evaluated using a sample of 100 documents, which may not capture all errors in the complete datasets.
- The translated USMLE evaluation sets measure performance on medical multiple-choice questions and do not establish clinical reliability.
- The fine-tuned models may produce incorrect or misleading medical information.

**These resources are intended for research and are not validated for clinical diagnosis, treatment decisions, or unsupervised patient care.**

## Availability and Licensing

The datasets and models are publicly available under the [Labadain account on Hugging Face](https://huggingface.co/labadain). The prompts and supporting reference files are maintained in this GitHub repository.

All the resources are released under the [Creative Commons Attribution-ShareAlike 4.0 International License](LICENSE).

The datasets are derived from existing medical resources, and the fine-tuned models depend on third-party base checkpoints. Users should consult the individual dataset and model cards for applicable source attribution, licensing information, and usage restrictions. The repository license does not supersede the terms governing upstream datasets or base models.

## Citation

If you use Labadain-MedQA, please acknowledge the resource and its original data sources. 
The citation for the associated Labadain-MedQA research paper will be added when its publication details are available.

## Feedback and Contributions

Researchers are welcome to report data errors, translation issues, documentation problems, or other findings through the [GitHub Issues](https://github.com/labadain/labadain-medqa/issues) page.