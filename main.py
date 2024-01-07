import os
from dotenv import load_dotenv
import logging

import asyncio
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, InlineQueryHandler

from openai import OpenAI
from supabase import create_client

from openai_calls import generate_response_3_5_turbo, get_embedding
from supabase_calls import update_interaction_supabase, query_supabase
from utils import extract_sentence
import instructor


load_dotenv()
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
instructor_client =instructor.patch(client)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def generate_response(message, user_name="Anonymous", supabase_response=None):
    """Generate a response from OpenAI."""
    joined_sentences = '\n'.join(supabase_response)
    logging.info(f"JOINED SENTENCES: {type(joined_sentences)}")
    user_message = f"USER MESSAGE:{message}\n\nRELATED CONTENT:{joined_sentences}"
    messages = [
        {"role": "system", "content": f"You are a helpful assistant who is speaking to cold leads for the technologist and writer, Julian Moses. Your goal is to connect them with the right content for the question they are asking, based on the content defined with the users message. You are speaking to a user with the username: {user_name}. Refer to them their username."},
        {"role": "user", "content": user_message}
    ]
    return generate_response_3_5_turbo(client, messages)

async def suggest_question(message):
    """Generate a response from OpenAI."""
    user_message = f"USER MESSAGE:{message}"
    messages = [
        {"role": "system", "content": f"You are a helpful assistant who is speaking to cold leads for the technologist and writer, Julian Moses. Your job is to suggest 3 questions the user can ask Julian about AI, Agriculture, and the pace of technology growth. As long as it is PG feel free to suggest other types of questions as well. Take the user messages into account<USERMESSAGE> {message}</USERMESSAGE>. Format the questions as such \n\n1. (Question1)\n1. (Question2)\n(Question3).\n\n"},
        {"role": "user", "content": user_message}
    ]

    res = await generate_response_3_5_turbo(client, messages)
    lines = res.split('\n')
    return lines

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_name = update.message.from_user.first_name
    supabase_chat_id = "julian"

    embedding = await get_embedding(client, user_message)
    supabase_response = await query_supabase(supabase, embedding, 5, supabase_chat_id)
    sentences = [extract_sentence(obj, 5) for obj in supabase_response.data]
    # Generate the OpenAI response and await it
    openai_response = await generate_response(user_message, user_name, sentences)
    # Send the awaited response as a message
    openai_response_text = await openai_response
    await context.bot.send_message(chat_id=update.effective_chat.id, text=openai_response_text)
    await update_interaction_supabase(update, openai_response)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

async def send_suggestions(update, suggestions):
    for i, suggestion in enumerate(suggestions, start=1):
        await update.message.reply_text(f"{suggestion}")


async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    suggestions = await suggest_question(user_message)

    # Call the asynchronous function to send suggestions
    await send_suggestions(update, suggestions)

async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")



if __name__ == '__main__':
    application = ApplicationBuilder().token(os.environ['TELEGRAM_TOKEN']).build()

    start_handler = CommandHandler('start', start)
    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    # caps_handler = CommandHandler('caps', caps)
    suggest_handler = CommandHandler('suggest', suggest)
    inline_caps_handler = InlineQueryHandler(inline_caps)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    
    
    application.add_handler(start_handler)
    application.add_handler(chat_handler)
    # application.add_handler(caps_handler)
    application.add_handler(suggest_handler)
    application.add_handler(inline_caps_handler)

    # Must be last
    application.add_handler(unknown_handler)
    
    application.run_polling()