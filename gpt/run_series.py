import os
import time
import fire
from interactive_conditional_samples import interact_model


def run_series(
        model_name="1558M",
        results_dir="samples",
        nsamples=5,
        prompts=[],
):
    if not prompts:
        for i in range(nsamples):
            prompt = input(f"Prompt {i + 1}: ")
            prompts.append(prompt)

    print("Starting series...")

    for prompt in prompts:
        print(f"\nGenerating from prompt #{prompts.index(prompt) + 1}...")
        interact_model(model_name=model_name, prompt=prompt,
                       filepath=os.path.join(results_dir,
                                             f"GPT-2 Sample on {time.strftime('%m-%d-%y %H %M %S')}.txt"))

    print("Finished series.")


if __name__ == '__main__':
    fire.Fire(run_series)
