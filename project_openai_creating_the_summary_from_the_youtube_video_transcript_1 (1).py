# Import necessary libraries
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import os
import datetime

# Retrieve the transcript for the specified video ID
transcript_list = YouTubeTranscriptApi.list_transcripts('y8S5VEYyKFM')
transcript = transcript_list.find_transcript(['en'])
transcript_fetched = transcript.fetch()

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"
openai_api_key = os.environ["OPENAI_API_KEY"]

# Initialize result and user prompt variables
result = ''
user_prompt = 'Divide into paragraphs'

# Define function to split transcript into chunks by time interval
def split_transcript_by_seconds(transcript_fetched, seconds):
    chunks = []
    current_chunk = []
    current_time = None

    for i, line_data in enumerate(transcript_fetched):
        line_time = datetime.timedelta(seconds=line_data['start'])

        # If current time interval is greater than specified interval, start new chunk
        if current_time is None:
            current_time = line_time
        if (line_time - current_time).total_seconds() > seconds:
            chunks.append(current_chunk)
            current_chunk = []
            current_time = line_time
        else:
            # If last line, add to current chunk and append to list
            if i == len(transcript_fetched) - 1:
                chunks.append(current_chunk)

        current_chunk.append(line_data['text'])

    return chunks

# Split transcript into chunks by specified time interval (300 seconds = 5 minutes)
chunks = split_transcript_by_seconds(transcript_fetched, 300)

# Iterate through each chunk and summarize using OpenAI API
for chunk in range(len(chunks)):
    transcript_texted = ' '.join(chunks[chunk])
    openai.api_key = openai_api_key
    prompt = f"\n\n{transcript_texted}\n Summarize the previous text\n"
    try:
        # Use OpenAI's text-curie-001 model to summarize chunk of transcript
        response = openai.Completion.create(
            model="text-curie-001",
            temperature=0.1,
            prompt=prompt,
            max_tokens=500
        )

        # Retrieve summary and append to result string
        summary = response.choices[0].text
        result += summary

    except openai.error.OpenAIError as error:
        # If there is an error with the OpenAI API, print the error message
        print(f"OpenAI API Error: {error}")

# Generate prompt for final summarization using OpenAI's text-davinci-003 model
if user_prompt == '':
    prompt = f'\n\n{result} \nTL;DR\n'
else:
    prompt = f'{result}\n\nTL;DR. And {user_prompt}\n'
response = openai.Completion.create(
    model="text-davinci-003",
    temperature=0.1,
    prompt=prompt,
    max_tokens=500
)

# Retrieve final summary
summary = response.choices[0].text

# Print final summary
print("Summarized Transcript: ", summary)

# Write intermediate result to file
filename = "output.txt"
with open(filename, 'w') as file:
    file.write(result)
