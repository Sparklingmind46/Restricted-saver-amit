import re
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
from io import BytesIO

# Initialize the bot with the API credentials
app = Client("my_bot", api_id="your_api_id", api_hash="your_api_hash")

# Regular expression to match Telegram public post links
POST_LINK_REGEX = r"https://t\.me/(\w+)/(\d+)"

# Dictionary to store user PDFs temporarily
user_pdfs = {}

# Function to handle the /start command (welcome message)
@app.on_message(filters.command("start"))
async def start(client, message):
    welcome_text = (
        "Welcome to the PDF Merge Bot! 🧑‍💻\n\n"
        "I can help you merge PDF files. Just send me your PDF files and use the /merge command "
        "to merge them.\n\n"
        "Also, if you send a public post link from a Telegram channel, I'll forward it to you!"
    )
    await message.reply(welcome_text)

# Function to handle received messages with post links
@app.on_message(filters.text)
async def handle_post_link(client, message):
    # Check if the message contains a valid post link
    match = re.match(POST_LINK_REGEX, message.text)
    if match:
        # Extract the channel username and post ID from the link
        channel_username = match.group(1)
        post_id = match.group(2)

        try:
            # Fetch the post from the channel using the channel username and post ID
            forwarded_message = await client.get_messages(channel_username, message_ids=post_id)
            
            # Forward the fetched message to the user's chat
            await client.forward_messages(chat_id=message.chat.id, from_chat_id=channel_username, message_ids=post_id)
        except Exception as e:
            # Handle exceptions (e.g., invalid link, bot lacks permission, etc.)
            await message.reply(f"Sorry, I couldn't fetch the post. Error: {str(e)}")

# Function to handle PDF file uploads
@app.on_message(filters.document)
async def handle_pdf(client, message):
    # Check if the document is a PDF
    if message.document.mime_type == "application/pdf":
        user_id = message.from_user.id
        
        # Initialize the PDF list if the user hasn't sent any PDFs yet
        if user_id not in user_pdfs:
            user_pdfs[user_id] = []

        # Download the PDF file
        file = await message.download()

        # Add the PDF to the user's list
        user_pdfs[user_id].append(file)

        # Notify the user that the PDF was received
        await message.reply("PDF file received! You can send more PDFs or type /merge to combine them.")

# Function to handle the /merge command
@app.on_message(filters.command("merge"))
async def merge_pdfs(client, message):
    user_id = message.from_user.id

    # Check if the user has any PDFs to merge
    if user_id not in user_pdfs or len(user_pdfs[user_id]) == 0:
        await message.reply("You haven't uploaded any PDFs yet! Please send PDFs first.")
        return

    # Prepare a PdfMerger object to merge the PDFs
    merger = PdfMerger()

    # Add all PDFs for the user to the merger
    for pdf_file in user_pdfs[user_id]:
        merger.append(pdf_file)

    # Create a BytesIO object to store the merged PDF
    merged_pdf = BytesIO()
    merger.write(merged_pdf)
    merged_pdf.seek(0)

    # Send the merged PDF back to the user
    await client.send_document(chat_id=message.chat.id, document=merged_pdf, caption="Here is your merged PDF!")

    # Clean up the temporary files and reset the user's list of PDFs
    merger.close()
    user_pdfs[user_id] = []

# Function to handle the /clear command (clear all PDFs for the user)
@app.on_message(filters.command("clear"))
async def clear_pdfs(client, message):
    user_id = message.from_user.id

    # Check if the user has any PDFs stored
    if user_id not in user_pdfs or len(user_pdfs[user_id]) == 0:
        await message.reply("You have no PDFs to clear.")
        return

    # Clear the user's PDF list
    user_pdfs[user_id] = []
    await message.reply("All your uploaded PDFs have been cleared.")

# Start the bot
app.run()
