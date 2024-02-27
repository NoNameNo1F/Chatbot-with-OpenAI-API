import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

list = ["https://api.openai.com/v1/chat/completions",
"https://api.openai.com/v1/audio/speech",
"https://api.openai.com/v1/audio/transcriptions",
"https://api.openai.com/v1/audio/translations",
"https://api.openai.com/v1/embeddings",
"https://api.openai.com/v1/fine_tuning/jobs",
"https://api.openai.com/v1/files",
"https://api.openai.com/v1/images/generations",
"https://api.openai.com/v1/models",
"https://api.openai.com/v1/moderations"]

client = OpenAI(
    api_key=os.environ.get("API_KEY")
)
def endpoint_chat_stream(client, message: str):
    # 1 Streaming API
    stream_endpoint = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": message
            }
        ],
        stream=True
    )
    return stream_endpoint
# 2 Audio Endpoints
def endpoint_audio_tts(client, message, voice):
    ## 2.1 Creating speech
    audio_file_path = Path(__file__).parent / "speech.mp3"

    text_to_speech = client.with_streaming_response.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="Is Typescript can do both BE and FE?"
    )
    text_to_speech.write_to_file(audio_file_path)
def endpoint_audio_transcript(client):
    ## 2.2 Creating transcription
    audio_file = open("speech.mp3", "rb")
    transcript_to_text = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    print(transcript_to_text["text"])
def endpoint_audio_translate(client):
    ## 2.3 Creating translation
    audio_file = open("speech.mp3", "rb")
    translate_to_text = client.audio.translations.create(
        model="whisper-1",
        file=audio_file
    )
    print(translate_to_text["text"])
# 3 Chat Endpoints
def endpoint_chat_completion(client, message:str):
    chat_completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an interviewer assistant that helps interviewee understand a clearly question, and give answer."},
        {"role": "user", "content": message}
    ]
    )
    print(chat_completion.choices[0].message)
# 4 Embeddings Endpoints
def endpoint_embedding(client, message):
    embbedings = client.embbedings.create(
        model="text-embbedings-ada-002",
        input="The food is suck",
        encoding_format="float"
    )
    print(embbedings["data"]["embedding"]) # this is an array
# 5 Fine-Tuning Endpoints
def endpoint_fine_tuning_create(client, file_id):
    # 5.1 Create a fine-tuning job
    fine_tuning = client.fine_tuning.jobs.create(
        training_file=file_id,
        model="gpt-3.5-turbo"
    )
    """ # Response of fine_tuning
    {
    "object": "fine_tuning.job",
    "id": "ftjob-abc123",
    "model": "gpt-3.5-turbo-0613",
    "created_at": 1614807352,
    "fine_tuned_model": null,
    "organization_id": "org-123",
    "result_files": [],
    "status": "queued",
    "validation_file": null,
    "training_file": "file-abc123",
    }
    """
    return fine_tuning
def endpoint_fine_tuning_list(client, file_id):
    # 5.2 List fine_tuning jobs
    fine_tuning_jobs = client.fine_tuning.jobs.list()
    return fine_tuning_jobs
def endpoint_fine_tuning_list_events(client, file_id):
    # 5.3 List fine_tuning job events
    fine_tuning_job_event = client.fine_tuning.jobs.list_events(
        fine_tuning_job_id=file_id,
        limit=2
    )
    return fine_tuning_job_event
def endpoint_fine_tuning_retrieve(client, file_id):
    # 5.4 Retrieve fine_tuning job
    fine_tuning_retrieve = client.fine_tuning.jobs.retrieve(file_id)
    return fine_tuning_retrieve
def endpoint_fine_tuning_cancel(client, file_id):
    # 5.5 Cancel a fine-tuning
    fine_tuning_job_cancel = client.fine_tuning.jobs.cancel(file_id)
    return fine_tuning_job_cancel
# 6 File Endpoints
def endpoint_file_create(client, file_name):
    # 6.1 Upload a file
    # up_file = client.files.create(
    #     file=open("mydatqa.json", "rb"),
    #     purpose="fine-tune"
    # )
    up_file = client.files.create(
        file=open(file_name, "rb"),
        purpose="fine-tune"
    )
    """
    {
    "id": "file-abc123",
    "object": "file",
    "bytes": 120000,
    "created_at": 1677610602,
    "filename": "mydata.jsonl",
    "purpose": "fine-tune",
    }
    """
    return up_file
def endpoint_file_create(client):
    # 6.2 List Files
    files = client.files.list()
    return files
def endpoint_file_retrieve(client, file_id):
    # 6.3 Retrieve File
    retrieve_file = client.files.retrieve(file_id)
    return retrieve_file
def endpoint_file_delete(client, file_id):
    # 6.4 Delete File
    del_file = client.files.delete(file_id)
    return del_file
def endpoint_file_create(client, file_id):
    # 6.5 Retrieve File content
    retrieve_content_file = client.files.content(file_id)
    return retrieve_content_file
# 7 Image Endpoints
def endpoint_image_generate(client, prompt, size, n):
    # 7.1 Create a Image
    create_img = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=n,
        size=size
    )
    return create_img.data[0].url
    #print(create_img['data']['url'])

def endpoint_image_edit(client, prompt, size, n):
    # 7.2 Edit a Image
    edit_img = client.images.edit(
        image=open("otter.png", "rb"),
        mask=open("mask.png", "rb"),
        prompt=prompt,
        n=n,
        size=size
    )
    #print(edit_img['data']['url'])
    return edit_img
def endpoint_image_edit(client, file_name, size, n):
    # 7.3 Variant of Image
    #image=open("image_edit_original.png", "rb"),
    vari_img = client.images.create_variation(
        image=open(file_name, "rb"),
        n=n,
        size=size
    )
    return vari_img
# 8 Models Endpoints
def endpoint_model_list(client):
    # 8.1 List available models
    models = client.models.list()
    return models
def endpoint_model_retrieve(client, model_id):
    # 8.2 Retrieve available models ("gpt-3.5-turbo-instruct")
    model = client.models.retrieve(model_id)
    return model
def endpoint_model_delete(client, model_id):
    # 8.2 Delete available models ("ft:gpt-3.5-turbo:acemeco:suffix:abc123")
    model = client.models.delete(model_id)
    return model
# 9 Moderations Endpoints
def endpoint_moderation_create(client):
    emotion = client.moderations.create(input="I want to kill them.")
    return emotion
def main():
    message = "How internet work?"
    response = endpoint_chat_stream(client,message)
    print(type(response))
    # for chunk in response:
    #     if chunk.choices[0].delta.content is not None:
    #         print(chunk.choices[0].delta.content, end="")


if __name__=="__main__":
    main()
