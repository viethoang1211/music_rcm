import gradio as gr
import gpt3
import webbrowser as wb
import re
from googleapiclient.discovery import build
import time
YOUTUBE_API_KEY = "YOUR_API_KEY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
PUBLIC= False

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
song_name= []
song_list= []
nothing = True
def search_youtube(query, max_results=1):
    # Call the search.list method to search for videos
    search_response = youtube.search().list(
        q=query,
        part="id",
        type="video",
        maxResults=max_results
    ).execute()

    video_links = []
    for search_result in search_response.get("items", []):
        # Generate the YouTube link for each search result
        if search_result["id"]["kind"] == "youtube#video":
            video_id = search_result["id"]["videoId"]
            video_link = f"https://www.youtube.com/watch?v={video_id}"
            video_links.append(video_link)
    # video_links.pop(0)
    return video_links

def get_song(text):
    global song_list, song_name
    try: 
        test_prompt = "find 4 popular songs based on this description " + str(text)
        resp = gpt3.Completion.create(prompt=test_prompt,chat=[])
        data = str(resp['text'])
        print(data)
        # pattern = r'"([^"]+)" by ([^\n\.-:]+)'
        pattern = r'"([^"]+)"'
        matches = re.findall(pattern, data)
        # song_names= [f"{song} - {singer}" for song, singer in matches]
        song_names = [f"{song} song" for song in matches]
        song_list =[]
        for x in song_names:
            tem = search_youtube(x)
            song_list.append(tem[0])
            time.sleep(1)
        # song_list = [search_youtube(song) for song in song_names]
        print(song_list)
        song_list = [x for x in song_list if len(x) > 0]
        song_list =list(set(song_list))
        wb.open(song_list[0])
        song_list.pop(0)
        return "success"
    except:
        return "fail"

def another_song():
    global song_list,nothing
    if len(song_list)>0:
        wb.open(song_list[0])
        song_list.pop(0)
        return "success"
    elif len(song_list) ==0:
        if nothing:
            return "Please tell more about what you want to hear"
        else:
            return "We have showed all the best available, please try with another prompt"

    
if __name__ == '__main__':
    with gr.Blocks() as interface:
        with gr.Row():
            text = gr.Text(label="Your song's name or describe what you want to hear", interactive=True)
        with gr.Row():
            submit = gr.Button("Submit")
        with gr.Row():
            another= gr.Button("Another song")
        with gr.Row():
            log = gr.Text(label="log", interactive=False)
        submit.click(get_song,inputs=[text],outputs=[log])
        another.click(another_song,inputs=[],outputs=[log])
        interface.launch(share=PUBLIC)
