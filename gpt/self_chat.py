import json
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import fire
import numpy as np
import tensorflow as tf

import encoder
import model
import sample


def self_chat(
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

        BOT1_NAME = "Tanmeet"
        BOT2_NAME = "Generic 16-year-old Anime Boy"

        # prompts do not reflect the opinions of the developer
        chat_hist = f"{BOT1_NAME}: Hello sexy...\n{BOT2_NAME}: Hello there..\n\n{BOT1_NAME} Are you horny?\n" \
                    f"{BOT2_NAME}: Oooh yes.."

        print(chat_hist + '\n')

        chat_hist += f"\n{BOT1_NAME}:"

        while True:
            # Process what Bot 1 should say
            context_tokens = enc.encode(chat_hist)

            out = sess.run(output, feed_dict={
                context: [context_tokens for _ in range(1)]
            })[:, len(context_tokens):]

            bot1_response = enc.decode(out[0])

            bot1_response = ''.join(bot1_response).split('\n', 1)[0]
            print(f"{BOT1_NAME}:" + bot1_response)

            chat_hist += f"{bot1_response}\n{BOT2_NAME}:"

            # Process what Bot 2 should say
            context_tokens = enc.encode(chat_hist)

            out = sess.run(output, feed_dict={
                context: [context_tokens for _ in range(1)]
            })[:, len(context_tokens):]

            bot2_response = enc.decode(out[0])

            bot2_response = ''.join(bot2_response).split('\n', 1)[0]
            print(BOT2_NAME + ':' + bot2_response + '\n')

            chat_hist += f"{bot2_response}\n{BOT1_NAME}:"


if __name__ == '__main__':
    fire.Fire(self_chat)
