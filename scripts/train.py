"""Model training pipeline — fine-tunes on generated EKR reasoning chains.

Formats each EKR as: domain | episode_type | context → reasoning_chain
Fine-tunes a small LM with LoRA on the RTX 3050 6GB GPU.
"""
import sys; sys.path.insert(0, "src")
import json
import random
from pathlib import Path

def format_ekr(ekr: dict) -> str:
    domain = ekr.get("domain", "GEN")
    ep_type = ekr.get("_episode_type", "unknown")
    reasoning = ekr.get("reasoning", [])
    decisions = ekr.get("decisions", [])
    evidence = ekr.get("evidence", [])
    atoms = ekr.get("knowledge_atoms", [])

    steps = "\n".join(
        f"  [{s.get('operation', 'Step')}] {s.get('content', '')}"
        for s in reasoning
    )
    dec_text = ""
    if decisions:
        dec_text = "\nDecisions:\n" + "\n".join(
            f"  - {d.get('decision', d.get('outcome', ''))}"
            for d in decisions
        )
    ev_text = f"\nEvidence: {len(evidence)} items" if evidence else ""

    return (
        f"<|domain|> {domain}\n"
        f"<|episode|> {ep_type}\n"
        f"<|reasoning|>\n{steps}"
        f"{dec_text}{ev_text}"
        f"\n<|atoms|> {len(atoms)}"
    )

def prepare_dataset(jsonl_path: str, output_dir: str, max_samples: int = 500_000):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    records = []
    with open(jsonl_path) as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    random.shuffle(records)
    records = records[:max_samples]
    split = int(len(records) * 0.95)
    train, val = records[:split], records[split:]

    with open(out / "train.jsonl", "w") as f:
        for r in train:
            f.write(json.dumps({"text": format_ekr(r)}) + "\n")
    with open(out / "val.jsonl", "w") as f:
        for r in val:
            f.write(json.dumps({"text": format_ekr(r)}) + "\n")
    print(f"Train: {len(train)}, Val: {len(val)}")
    return len(train), len(val)

def train(
    model_name: str = "HuggingFaceTB/SmolLM2-360M",
    output_dir: str = "build/v0.4/model",
    data_dir: str = "build/v0.4/data",
    num_epochs: int = 1,
    batch_size: int = 4,
    max_length: int = 512,
):
    import torch
    from transformers import (
        AutoModelForCausalLM, AutoTokenizer,
        TrainingArguments, Trainer, DataCollatorForLanguageModeling,
    )
    from datasets import load_dataset

    dataset = load_dataset(
        "json", data_files={
            "train": f"{data_dir}/train.jsonl",
            "validation": f"{data_dir}/val.jsonl",
        }
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def tokenize(examples):
        return tokenizer(
            examples["text"], truncation=True, max_length=max_length,
            padding="max_length",
        )

    tokenized = dataset.map(tokenize, batched=True, remove_columns=["text"])

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, device_map="auto",
    )

    # LoRA for memory efficiency
    from peft import LoraConfig, get_peft_model, TaskType
    lora_config = LoraConfig(
        r=8, lora_alpha=16, target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05, bias="none", task_type=TaskType.CAUSAL_LM,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        evaluation_strategy="steps",
        eval_steps=500,
        save_steps=1000,
        logging_steps=100,
        learning_rate=2e-4,
        warmup_steps=100,
        fp16=True,
        report_to="none",
        save_total_limit=2,
        remove_unused_columns=False,
        dataloader_num_workers=0,
    )

    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        data_collator=collator,
    )

    trainer.train()
    trainer.save_model(f"{output_dir}/final")
    tokenizer.save_pretrained(f"{output_dir}/final")
    print(f"Model saved to {output_dir}/final")
    eval_results = trainer.evaluate()
    print(f"Eval perplexity: {torch.exp(torch.tensor(eval_results['eval_loss'])):.2f}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true", help="Prepare dataset from generated JSONL")
    parser.add_argument("--train", action="store_true", help="Run training")
    parser.add_argument("--jsonl", default="build/v0.4/dataset_1m.jsonl")
    parser.add_argument("--model", default="HuggingFaceTB/SmolLM2-360M")
    parser.add_argument("--samples", type=int, default=100_000)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch", type=int, default=4)
    args = parser.parse_args()

    if args.prepare:
        prepare_dataset(args.jsonl, "build/v0.4/data", max_samples=args.samples)
    if args.train:
        train(
            model_name=args.model, num_epochs=args.epochs,
            batch_size=args.batch,
        )
