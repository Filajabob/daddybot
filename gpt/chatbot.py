import json
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import fire
import numpy as np
import tensorflow as tf

import encoder
import model
import sample


def conversation(
        model_name='124M',
        seed=None,
        length=20,
        temperature=0.75,
        top_k=0,
        top_p=1,
        models_dir='models'
):
    print("Loading model and hyperparameters...")

    models_dir = os.path.expanduser(os.path.expandvars(models_dir))

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()

    with open(os.path.join('..\\' + models_dir, model_name, 'hparams.json')) as f:
        hparams = json.load(f)

    if length is None:
        length = hparams["n_ctx"] // 2
    elif length > hparams["n_ctx"]:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    print("Starting session...")
    with tf.compat.v1.Session(graph=tf.Graph()) as sess:
        context = tf.compat.v1.placeholder(tf.int32, [1, None])
        np.random.seed(seed)
        tf.compat.v1.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=1,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.compat.v1.train.Saver()
        ckpt = tf.train.latest_checkpoint('..\\' + os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)

        print("Auto-starting conversation...\n")
        chat_hist = "Human: Hello\nAI: Hello human!"

        print("You: Hello\nAI: Hello human!")

        while True:
            query = input("You: ")

            while not query:
                query = input("You: ")

            raw_text = chat_hist + f"\nHuman: {query}\nAI:"

            context_tokens = enc.encode(raw_text)

            out = sess.run(output, feed_dict={
                context: [context_tokens for _ in range(1)]
            })[:, len(context_tokens):]

            text = enc.decode(out[0])

            result = list(text)

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

            ai_response = ''.join(result).split('\n', 1)[0]
            print("AI:" + ai_response)

            chat_hist += f"\nHuman: {query}\nAI:{ai_response}"


if __name__ == '__main__':
    fire.Fire(conversation)
