from flask import Flask, render_template, request
import iss

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



if __name__ == '__main__':
    app.run(debug=True)

