from flask import Flask, render_template, request, flash
import pandas as pd
import iss
import twtr
import json

app = Flask(__name__)
app.secret_key = 'youllneverguess'

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
    time_limit = None
    show_time = None
    show_tweets = None
            
    if request.method == 'POST':
        kwd = request.form.get('kwd')
        kwd_clean = kwd.split(',')
        kwd_clean = [k.strip() for k in kwd_clean]
        time_limit = float(request.form.get('time_limit')) * 60
        
        if time_limit < 60:
            show_time = '{} seconds'.format(time_limit)
        elif time_limit > 60:
            show_time = '{} minutes'.format(time_limit / 60)
        else:
            show_time = '1 minute'
            
        print("kwd: {}, type: {}".format(kwd_clean, type(kwd_clean)))
        print("time_limit: {}, type: {}".format(time_limit, type(time_limit)))
        
        twtr.get_live(kwd_clean, time_limit = time_limit)
        show_tweets = twtr.clean_and_analyse('streamer_listened.json')
        
    # Flatten the tweets and store in `tweets`
    
    return render_template(
        'twitter_live.html',
        kwd=kwd,
        time_limit=time_limit,
        show_time=show_time,
        show_tweets=show_tweets.tweet_text.values if show_tweets is not None else None,#['{} \n'.format(f) for f in show_tweets['tweet_text']],
        title = 'Live Tweets'
    )

@app.route('/twt_hist', methods=['GET', 'POST'])
def twt_hist():
    kwd = None
    show_tweets = None
    result_type = None
    
    if request.method == 'POST':
        kwd = request.form.get('kwd')
        kwd_clean = kwd.split(',')
        kwd_clean = [k.strip() for k in kwd_clean]
        result_type = request.form.get('result_type')
        print("kwd: {}, type: {}".format(kwd_clean, type(kwd_clean)))
        print("result_type: {}, type: {}".format(result_type, type(result_type)))
        twtr.get_historical(kwd_clean, result_type)
        show_tweets = twtr.clean_and_analyse('cursor_historical.json')
    
    # Print out the first 5 tweets from this dataset
    #print(ds_tweets['text'].values[0:5])
    #res = twtr.get_historical(kwd = ['#brexit']) #get_historical
    
    
    return render_template(
        'twitter_hist.html',
        kwd=kwd,
        result_type=result_type.capitalize() if result_type is not None else None,
        show_tweets=show_tweets.tweet_text.values if show_tweets is not None else None,
        title = 'Historical Tweets'
    )





if __name__ == '__main__':
    app.run(debug=True)

