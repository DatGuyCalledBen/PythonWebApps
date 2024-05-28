import os
import sys
import platform
import socket
import hashlib
import datetime
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from flask import Flask, Response

# Initialize Flask application
application = Flask(__name__)

@application.route('/')
def home():
    # Basic system information
    message = '<h1>Python WSGI Test Application</h1>'
    version_info = f'<p>Python Version: {platform.python_version()}</p>'
    os_info = f'<p>Operating System: {platform.platform()}</p>'
    hostname = f'<p>Hostname: {socket.gethostname()}</p>'
    response = f'{message}{version_info}{os_info}{hostname}'

    # String manipulation examples
    response += f'<p>Reversed String: {"hello world"[::-1]}</p>'
    response += f'<p>Uppercase String: {"hello world".upper()}</p>'

    # Data structure examples
    response += f'<p>List Sum: {sum([1, 2, 3, 4, 5])}</p>'
    response += f'<p>Dictionary Keys: {", ".join({"a": 1, "b": 2, "c": 3}.keys())}</p>'

    # Current datetime
    response += f'<p>Current Time: {datetime.datetime.now()}</p>'

    # MD5 hash example
    response += f'<p>MD5 Hash of "test": {hashlib.md5("test".encode()).hexdigest()}</p>'

    # Data Science Workflow
    # Step 1: Data Collection
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
    df = pd.read_csv(url)
    df['species'] = df['species'].astype('category').cat.codes

    # Step 2: Exploratory Data Analysis (EDA) Visualization
    plt.figure(figsize=(10, 6))
    plt.scatter(df['sepal_length'], df['sepal_width'], c='blue', label='Sepal')
    plt.scatter(df['petal_length'], df['petal_width'], c='red', label='Petal')
    plt.xlabel('Length')
    plt.ylabel('Width')
    plt.title('Sepal and Petal Length vs Width')
    plt.legend()

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    plot_url = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('utf-8')
    response += f'<h2>Data Visualization</h2><img src="{plot_url}">'

    # Step 3: Feature Engineering
    X = df.drop('species', axis=1)
    y = df['species']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Step 4: Predictive Modeling
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Model Evaluation Results
    response += f'<h2>Model Evaluation</h2><ul>'
    response += f'<li>Mean Squared Error: {mse}</li>'
    response += f'<li>R-squared: {r2}</li>'
    response += '</ul>'

    return Response(response, mimetype='text/html')

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
