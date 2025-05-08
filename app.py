from flask import Flask, render_template, request
import joblib
from models.vendor_classifier import predict_category

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    vendor = request.form['vendor']
    category = predict_category(vendor)
    return render_template('result.html', vendor=vendor, category=category)

if __name__ == '__main__':
    app.run(debug=True)
