
import os

#mp3 to wave
import subprocess

#flask setup
from flask import Flask, flash, request, redirect, render_template
#speech recognization
import speech_recognition as sr
r = sr.Recognizer()
#openai completion setup
import openai
openai.api_key = "API KEY"

UPLOAD_FOLDER = 'files'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/',methods=["GET","POST"])
def root():
    if request.method =="POST":
        storydata = request.form.get("story")
        file1 = open("files/textfiles/audio.txt", "w")
        file1.writelines(storydata)
        file1.close()
        #get data from completion file
        file2 = open("files/textfiles/completion.txt", "r")
        completiondata = file2.read()
        file2.close()
        #and clear the completion data every time
        file5 = open("files/textfiles/completion.txt","r+")
        file5.truncate(0)
        file5.close()
        if completiondata:
            storydata = storydata + completiondata
    elif request.method=="GET":
        storydata="Hi. I'll tell you a story about " 
        file1 = open("files/textfiles/audio.txt","r+")
        file1.truncate(0)
        file1.close()     
    return render_template("index.html",storydata=storydata)


@app.route('/save-record', methods=['POST'])
def save_record():
    #deleting testig.wav if already exists
    wavname = "files/testing.wav"
    if os.path.exists(wavname):
        os.remove(wavname)
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    file_name = "testing" + ".mp3"
    full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file.save(full_file_name)
    
    #converting to wav
    
    subprocess.call(['ffmpeg', '-i', 'files/testing.mp3',
                 wavname],shell=True)
    #getting text from wav file
    hellow=sr.AudioFile(wavname)
    with hellow as source:
        audio = r.record(source)
    try:
        user_audio = r.recognize_google(audio)
 
    except Exception as e:
        #flash("sound not clear. please try again")
        print("Exception: "+str(e))
    #we will take few words from the story and audio input together as openai input for more accurate result
    file3 = open("files/textfiles/audio.txt","r")
    file_obj = file3.read()
    file3.close()
    if len(file_obj)>100:
        openai_input = file_obj[-100:] + user_audio
    else:
        openai_input = file_obj + user_audio   

    #openai
    res= openai.Completion.create(
    engine="text-davinci-001",
    prompt=openai_input,
    temperature= 0.90,
    max_tokens=50
    )

    op = res.choices[0]["text"]
    oplist = list(op.split())
    #saving user input and openai response in textfile
    L = user_audio+" "+ " ".join(oplist)
    file1 = open("files/textfiles/completion.txt", "w")
    file1.writelines(L)
    file1.close()

    
    

    #return
    return "<h1>StoryGenerator</h1>"



if __name__ == '__main__':
    app.run(debug=True)