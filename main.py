from flask import Flask, render_template, request
import pandas as pd
import iss
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

@app.route('/twt_live', methods=['GET', 'POST'])
def twt_live():
    kwd = None
    tweets_to_show = None
    # time_limit
    
    if request.method == 'POST':
        kwd = request.form.get('kwd')
        kwd_clean = kwd.split(',')
        kwd_clean = [k.strip() for k in kwd_clean]
        print("kwd: {}, type: {}".format(kwd_clean, type(kwd_clean)))
        # twtr.get_live(kwd_clean)

    # Flatten the tweets and store in `tweets`
    tweets = pd.DataFrame(twtr.flatten_tweets('streamer_listened.json'))
    
    # Print out the first 5 tweets from this dataset
    #print(ds_tweets['text'].values[0:5])
    #res = twtr.get_historical(kwd = ['#brexit']) #get_historical
    
    return render_template(
        'twitter.html',
        kwd=kwd,
        tweets_to_show=tweets['text'],
        title = 'Live Tweets'
    )

@app.route('/twt_hist', methods=['GET', 'POST'])
def twt_hist():
    kwd = None
    tweets_to_show = None
    # time_limit
    
    if request.method == 'POST':
        kwd = request.form.get('kwd')
        kwd_clean = kwd.split(',')
        kwd_clean = [k.strip() for k in kwd_clean]
        print("kwd: {}, type: {}".format(kwd_clean, type(kwd_clean)))
        twtr.get_historical(kwd_clean)

    # Flatten the tweets and store in `tweets`
    tweets = pd.DataFrame(twtr.flatten_tweets('cursor_historical.json'))
    
    # Print out the first 5 tweets from this dataset
    #print(ds_tweets['text'].values[0:5])
    #res = twtr.get_historical(kwd = ['#brexit']) #get_historical
    
    return render_template(
        'twitter.html',
        kwd=kwd,
        tweets_to_show=tweets['text'],
        title = 'Historical Tweets'
    )



if __name__ == '__main__':
    app.run(debug=True)

