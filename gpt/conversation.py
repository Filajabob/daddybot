import json
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import tensorflow as tf

from gpt import encoder
from gpt import model
from gpt import sample


async def conversation(ctx, client):
    await ctx.respond("Getting things ready...")

    model_name = '124M'
    seed = None
    length = 20
    temperature = 0.765
    top_k = 0
    top_p = 1
    models_dir = 'gpt/models'

    models_dir = os.path.expanduser(os.path.expandvars(models_dir))

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()

    with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
        hparams = json.load(f)

    if length is None:
        length = hparams["n_ctx"] // 2
    elif length > hparams["n_ctx"]:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

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
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)

        chat_hist = "Human: Hello\nAI: Hello human!"

        def check(msg):
            if msg.author.id == ctx.author.id:
                return msg.content
            else:
                return None

        await ctx.send("Chatbot is ready.\nSome content the bot sends may be inappropriate or offensive. Use at your "
                       "own risk.\nTo end your conversation, send 'quit'")

        while True:
            query = await client.wait_for('message', check=check)

            query = query.content

            if query == "quit":
                await ctx.send("Goodbye!")
                break

            await ctx.trigger_typing()
            raw_text = chat_hist + f"\nHuman: {query}\nAI:"

            context_tokens = enc.encode(raw_text)

            out = sess.run(output, feed_dict={
                context: [context_tokens for _ in range(1)]
            })[:, len(context_tokens):]

            text = enc.decode(out[0])

            ai_response = text.split('\n', 1)[0]
            chat_hist += f"\nHuman: {query}\nAI:{ai_response}"

            await ctx.send(ai_response)