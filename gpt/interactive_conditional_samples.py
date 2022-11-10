#!/usr/bin/env python3

import json
import os
import time
import datetime

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import fire
import numpy as np
import tensorflow as tf

import encoder
import model
import sample


def interact_model(
        model_name='1558M',
        seed=None,
        nsamples=1,
        batch_size=1,
        length=None,
        temperature=0.75,
        top_k=0,
        top_p=1,
        models_dir='models',
        filepath=None,
        prompt=None,
        prompt_filepath=None
):
    """
    Interactively run the model
    :model_name=124M : String, which model to use
    :seed=None : Integer seed for random number generators, fix seed to reproduce
     results
    :nsamples=1 : Number of samples to return total
    :batch_size=1 : Number of batches (only affects speed/memory).  Must divide nsamples.
    :length=None : Number of tokens in generated text, if None (default), is
     determined by model hyperparameters
    :temperature=1 : Float value controlling randomness in boltzmann
     distribution. Lower temperature results in less random completions. As the
     temperature approaches zero, the model will become deterministic and
     repetitive. Higher temperature results in more random completions.
    :top_k=0 : Integer value controlling diversity. 1 means only 1 word is
     considered for each step (token), resulting in deterministic completions,
     while 40 means 40 words are considered at each step. 0 (default) is a
     special setting meaning no restrictions. 40 generally is a good value.
     :models_dir : path to parent folder containing model subfolders
     (i.e. contains the <model_name> folder)
     :filepath : txt file where the results should be printed to. All directories must exist.
     :prompt : The prompt for the sample(s). If None, will ask via user input.
     :prompt_filepath : A txt file that contains a prompt.
    """
    models_dir = os.path.expanduser(os.path.expandvars(models_dir))
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()

    with open(os.path.join('..\\' + models_dir, model_name, 'hparams.json')) as f:
        hparams = json.load(f)

    if length is None:
        length = hparams["n_ctx"] // 2
    elif length > hparams["n_ctx"]:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.compat.v1.Session(graph=tf.Graph()) as sess:
        context = tf.compat.v1.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.compat.v1.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.compat.v1.train.Saver()
        ckpt = tf.train.latest_checkpoint('..\\' + os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)

        while True:
            if not prompt and not prompt_filepath:
                raw_text = input("Model prompt >>> ")

                while not raw_text:
                    print('Prompt should not be empty!')
                    raw_text = input("Model prompt >>> ")

            elif prompt_filepath:
                with open(prompt_filepath, 'r') as f:
                    raw_text = f.read()

            else:
                raw_text = prompt

            start = time.time()

            print("Generating...")

            context_tokens = enc.encode(raw_text)
            generated = 0

            for _ in range(nsamples // batch_size):
                out = sess.run(output, feed_dict={
                    context: [context_tokens for _ in range(batch_size)]
                })[:, len(context_tokens):]

                for i in range(batch_size):
                    generated += 1
                    text = enc.decode(out[i])

                    # Printing stuff

                    if not filepath:
                        print("=" * 40 + " SAMPLE " + str(generated) + " " + "=" * 40)

                    result = list(raw_text + text)

                    line_placement = 1
                    index = 0

                    for letter in result:
                        if line_placement >= 120 and letter.isspace():
                            result[index] = '\n'
                            line_placement = 1
                        elif letter == '\n':
                            line_placement = 1

                        line_placement += 1
                        index += 1

                    if not filepath:
                        print(''.join(result))
                    else:
                        with open(filepath, 'w') as f:
                            f.write("=" * 40 + " SAMPLE " + str(generated) + " " + "=" * 40 +
                                    '\n' + ''.join(result) + '\n' + '=' * 80)

            if not filepath:
                print("=" * 80)

            print(f"Generation finished after {round(time.time() - start, 2)} secs.")

            if prompt or prompt_filepath:
                break


if __name__ == '__main__':
    fire.Fire(interact_model)
