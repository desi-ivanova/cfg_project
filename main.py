from flask import Flask, render_template, request
import iss
from tweepy import OAuthHandler
from tweepy import API
import twtr
import json

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World'

'''
@app.route('/<name>')
def hello_someone(name):
    return render_template('hello.html', name=name.title())
'''

@app.route('/iss', methods=['GET','POST'])
def iss_main():
    current_location = iss.get_iss_location()
    pass_time = None
    postcode = None

    if request.method == 'POST':
        postcode = request.form.get('postcode')
        pass_time = iss.get_iss_pass_time_from_postcode(postcode)

    return render_template(
        'iss.html',
        current_location=current_location,
        pass_time=pass_time,
        postcode=postcode
    )

@app.route('/twt',)
def twt_main():
    # Consumer key authentication
    auth = OAuthHandler('POtvWDXl74vOtKxgK00oJZGWx', 'L1ASG7vlTwTWTbVHxgdkNgNoeejYPhT7tDu8H5LuELO0fae8IW')

    # Access key authentication
    auth.set_access_token('2909167113-et0k0ZVAxEalFyP9BRoJPKD2S9sIQqyGXcClRcC', 'A19IdhhZLEEhv0mj3dWPMp6G8RRxHZXUw01jDlpVHhmYl')

    # Set up the API with the authentication handler
    api = API(auth)

    from tweepy import Stream

    # Set up words to track
    keywords_to_track = ['#brexit', '#referendum', '#nodeal', '#maybot', '#theresamay', '#jeremycorbyn', 
                         '#peoplesvote', '#letwin', '#tory', 'Boris Johnson', 'Theresa May', '#indicativevotes']

    # Instantiate the SListener object 
    listen = twtr.SListener(api, time_limit=10)

    # Instantiate the Stream object
    stream = Stream(auth, listen)

    # Begin collecting data
    stream.filter(track = keywords_to_track)

    with open('streamer_test.json') as fp:
        cnt = 0
        while cnt < 2:
            # print("Line {}: {} \n".format(cnt, line.strip()))
            # print("JSON: {}".format(json.loads(line)))
            line = json.loads(fp.readline())
            print(line['text'])
            print('\n')
            cnt += 1

    return(line)

if __name__ == '__main__':
    app.run(debug=True)

