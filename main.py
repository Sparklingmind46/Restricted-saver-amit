import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from PyPDF2 import PdfMerger
import tempfile

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch API ID, API HASH, and BOT TOKEN from environment variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Check if the environment variables are set correctly
if not API_ID or not API_HASH or not BOT_TOKEN:
    logger.error("API_ID, API_HASH, or BOT_TOKEN are not set in the environment variables!")
    exit(1)

# Create Pyrogram User Client for public channel access
user_client = Client("user_session", api_id=API_ID, api_hash=API_HASH)

# Create Pyrogram Bot Client for bot functionality
bot_client = Client("bot_session", bot_token=BOT_TOKEN)

# Temporary storage for PDFs
pdf_files = []

# Command to start the bot and welcome message
@bot_client.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("Welcome! Send me a link to a public post or a PDF to merge.")

# Command to merge PDFs
@bot_client.on_message(filters.command("merge"))
async def merge_pdfs(client, message):
    if len(pdf_files) < 2:
        await message.reply("Please send at least two PDFs to merge.")
        return

    merger = PdfMerger()

    # Merge all the PDFs in the list
    for pdf in pdf_files:
        merger.append(pdf)

    # Save the merged PDF to a temporary file
    merged_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(merged_pdf.name)
    merger.close()

    # Send the merged PDF back to the user
    with open(merged_pdf.name, "rb") as f:
        await message.reply_document(f)

    # Clean up the temporary PDF file
    os.remove(merged_pdf.name)
    pdf_files.clear()

# Command to clear stored PDFs
@bot_client.on_message(filters.command("clear"))
async def clear_pdfs(client, message):
    pdf_files.clear()
    await message.reply("All stored PDFs have been cleared.")

# Function to handle public post link and send it back
@bot_client.on_message(filters.regex(r"https?://t.me/[\w+]+/[\d]+"))
async def send_public_post(client, message):
    post_link = message.text
    channel_username = post_link.split("/")[3]  # Extract channel username
    post_id = post_link.split("/")[-1]  # Extract post ID

    try:
        # Fetch the message from the public channel using user client
        async with user_client:
            public_message = await user_client.get_messages(channel_username, message_ids=int(post_id))

        # Forward the message to the user
        await message.reply(public_message.text or "No text content in this post.")
    
    except Exception as e:
        logger.error(f"Error fetching public post: {e}")
        await message.reply("Sorry, I couldn't fetch the post. Please check the link.")

# Handle PDF files uploaded by the user
@bot_client.on_message(filters.document)
async def handle_pdf(client, message: Message):
    if message.document.mime_type == "application/pdf":
        file_path = await message.download()
        pdf_files.append(file_path)
        await message.reply("PDF added to the merge list.")

# Run the bot
if __name__ == "__main__":
    bot_client.run()