from typing import Final
import re
import os
# pip install python-telegram-bot
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO
from compress_image import compress_image
from handle_response import handle_response
from compress_video import compress_video
from crawl_website import crawl_website
from extract_article import extract_article
from dotenv import load_dotenv

load_dotenv('keys.env')

# Define a regular expression to check for URLs
url_pattern = re.compile(r'https?://\S+')
def contains_url(message):
    return bool(url_pattern.search(message.text))

print('Starting up bot...')

TOKEN: Final = os.getenv('MY_TOKEN_KEY')
BOT_USERNAME: Final = os.getenv('MY_BOT_ID')


# Lets us use the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! I\'m intelliBot. What\'s up?')


# Lets us use the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('intelliBot can help you in \n1.chat-gpt search\n2.Image Compression\n3.Web crawler\n4.Article Extraction')

# Lets us use the /compress_image command
async def compress_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Now send an image to compress')
    context.user_data['compressing_image'] = True

# Lets us use the /compress_video command
async def compress_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Now send a video to compress')
    context.user_data['compressing_video'] = True

# Lets us use the /web_crawler command
async def web_crawler_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Now send a website page link')
    context.user_data['web_crawler'] = True

# Lets us use the /article_extractor command
async def article_extractor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Now send a website page link to extract an article')
    context.user_data['article_extractor'] = True


#handle the responses

async def handle_compressed_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'compressing_image' in context.user_data and context.user_data['compressing_image']:
        # Check if the message contains a photo
        if update.message.photo:
            # Get the photo file ID
            file_id = update.message.photo[-1].file_id
            # Get the file object by file ID
            file = await context.bot.get_file(file_id)
            # Download the photo as bytes
            image_bytes = await file.download_as_bytearray()

            # Compress the image
            compressed_image_bytes = compress_image(image_bytes)

            # Send the compressed image back to the user
            await update.message.reply_photo(BytesIO(compressed_image_bytes), caption='Image compressed!')
        else:
            await update.message.reply_text('Please send a valid image.')

        # Reset the flag after processing the image
        context.user_data['compressing_image'] = False
    else:
        await update.message.reply_text('I am not currently compressing an image. Use /compress_image to start the process.')


async def handle_compressed_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'compressing_video' in context.user_data and context.user_data['compressing_video']:
        # Check if the message contains a video
        if update.message.video:
            # Get the video file ID
            file_id = update.message.video.file_id
            # Get the file object by file ID
            file = await context.bot.get_file(file_id)
            # Download the video as bytes
            video_bytes = await file.download_as_bytearray()

            # Compress the video (you need to implement your own video compression logic)
            compressed_video_bytes = compress_video(video_bytes)

            # Send the compressed video back to the user
            await update.message.reply_video(BytesIO(compressed_video_bytes), caption='Video compressed!')
        else:
            await update.message.reply_text('Please send a valid video.')

        # Reset the flag after processing the video
        context.user_data['compressing_video'] = False
    else:
        await update.message.reply_text('I am not currently compressing a video. Use /compress_video to start the process.')


async def handle_crawled_data(update: Update, context:ContextTypes.DEFAULT_TYPE):
    if 'web_crawler' in context.user_data and context.user_data['web_crawler']:
        # Check if the message contains a URL using the regular expression
        if url_pattern.search(update.message.text):
            url = url_pattern.search(update.message.text).group()
            await update.message.reply_text(f'Crawling data from {url}')

            crawled_data = crawl_website(url)
            # Iterate through each link and send it as a separate message
            for link in crawled_data:
                # Send the link as a message
                await update.message.reply_text(f'\n{link}')

            # Reset the flag in user_data
            context.user_data['web_crawler'] = False
        else:
            await update.message.reply_text('The provided message does not contain a valid URL or you have not run the command.')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get basic info of the incoming message
    message_type: str = update.message.chat.type
    text: str = update.message.text
    context.user_data['compressing_image'] = False
    context.user_data['compressing_video'] = False
    context.user_data['web_crawler'] = False
    # Print a log for debugging
    print(f'User ({update.message.chat.id}) {update.message.from_user.first_name} {update.message.from_user.last_name} in {message_type}: "{text}"')

    # React to group messages only if users mention the bot directly
    if message_type == 'group':
        # Replace with your bot username
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return  # We don't want the bot respond if it's not mentioned in the group
    else:
        response: str = handle_response(text)

    # Reply normal if the message is in private
    print('Bot:', response)
    await update.message.reply_text(response)

async def handle_extracted_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    if 'article_extractor' in context.user_data and context.user_data['article_extractor']:
       # Check if the message contains a URL using the regular expression
        if url_pattern.search(update.message.text):
            url = url_pattern.search(update.message.text).group()
            await update.message.reply_text(f'Extracting article from {url}')

            article_content = extract_article(url)
        # Save the article content to a .txt file
        file_name = "extracted_article.txt"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(article_content)

        # Send the .txt file to the user
        with open(file_name, "rb") as file:
            await context.bot.send_document(chat_id=chat_id, document=file)

        # Clean up: Remove the temporary file
        os.remove(file_name)

        # Reset the flag in user_data
        context.user_data['article_extractor'] = False
    else:
        await update.message.reply_text('The article extraction process is not active.')

def wrapped_handle_crawled_data(update, context):
    if 'web_crawler' in context.user_data and context.user_data['web_crawler']:
        return handle_crawled_data(update, context)
    elif 'article_extractor' in context.user_data and context.user_data['article_extractor']:
        return handle_extracted_article(update,context)
    else:
        return handle_message(update,context)

# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('compress_image', compress_image_command))
    # app.add_handler(CommandHandler('compress_video',compress_video_command))
    app.add_handler(CommandHandler('web_crawler', web_crawler_command))
    app.add_handler(CommandHandler('article_extractor',article_extractor_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, wrapped_handle_crawled_data))
    app.add_handler(MessageHandler(filters.PHOTO, handle_compressed_image))
    # app.add_handler(MessageHandler(filters.VIDEO, handle_compressed_video))
    app.add_error_handler(error)

    print('Polling...')
    # Run the bot
    app.run_polling(poll_interval=3)
