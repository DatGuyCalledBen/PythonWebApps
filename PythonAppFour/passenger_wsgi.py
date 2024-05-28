import os
import platform
import socket
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, Response

# Initialize Flask application
application = Flask(__name__)

@application.route('/')
def home():
    # Basic system information
    message = '<h1>Rocket Simulation</h1>'
    version_info = f'<p>Python Version: {platform.python_version()}</p>'
    os_info = f'<p>Operating System: {platform.platform()}</p>'
    hostname = f'<p>Hostname: {socket.gethostname()}</p>'
    response = f'{message}{version_info}{os_info}{hostname}'

    # Rocket simulation script
    Mr = 10000
    IMp = 200000
    K = 1000
    Ve = 5100
    G = 9.8
    i = 89.94
    t = 0.005
    T = 1500
    dim = [int((T/t)+1), 16]

    data = np.zeros(dim)

    def Xx(n):
        data[n,0] = data[n-1,0] + t*data[n-1,7]

    def Xy(n):
        data[n,1] = data[n-1,1] + t*data[n-1,8]

    def Vx_instant(n):
        data[n, 7] = data[n,2] + (t/2)*data[n,14]

    def Vy_instant(n):      
        data[n, 8] = data[n,3] + (t/2)*data[n,15]

    def Vx(n):
        if n > 0:
            data[n, 2] = data[n-1,7] + (t/2)*data[n,14] 
        else:
            data[n, 2] = (t/2)*data[n,14]

    def Vy(n):
        if n > 0:
            data[n,3] = data[n-1, 8] + (t/2)*data[n,15]
        else:
            data[n,3] = (t/2)*data[n,15]

    def Fx(n):
        if data[n,4] > 0:
            data[n,9] = Ve*K*np.cos(data[n,6]) 
        else:
            data[n,9] = 0

    def Fy(n):
        if data[n,4] > 0:
            data[n,10] = Ve*K*np.sin(data[n,6]) - G*data[n,5]*1.04151
        else:
            data[n,10] = -G*data[n,5]*1.04151

    def M(n):
        data[n, 5] = Mr + data[n, 4]

    def Mp(n):
        if n > 0:
            if data[n-1,4] > 0:
                data[n,4] = data[n-1, 4] - K/200
            else:
                data[n,4] = 0
        else:
            data[n,4] = IMp

    def θ(n):
        if n > 0:
            if data[n,3] == 0:
                data[n,6] = np.arctan(data[n-1,8]/data[n-1, 7])
            else:
                data[n,6] = np.arctan(data[n,3]/data[n,2])
        else:
            data[n,6] = np.radians(i)

    def time(n):
        data[n,13] = n*t

    def Ax(n):
        data[n,14] = (1/data[n,5])*data[n,9]

    def Ay(n):
        data[n,15] = (1/data[n,5])*data[n,10]

    X = int(T/t)
    for n in range(X):
        Mp(n)
        M(n)
        θ(n)
        Fx(n)
        Fy(n)
        Ax(n)
        Ay(n)
        Vx(n)
        Vy(n)
        Vx_instant(n)
        Vy_instant(n)
        Xx(n+1)
        Xy(n+1)
        Mp(n+1)
        M(n+1)
        θ(n+1)
        Fx(n+1)
        Fy(n+1)
        Vx(n+1)
        Vy(n+1)
        time(n)
        if data[n,1] < 0:
            X = n
            break

    duration_mins = int((X*t)/60)
    duration_secs = int(float(X*t - (int((X*t)/60))*60))
    peak = np.max(data[:,1])/1000
    edge = np.max(data[:,0])/1000
    length = np.trapz(data[:X,1]/1000, data[:X,0]/1000)

    flight_info = f'<h2>Flight Information</h2><ul>'
    flight_info += f'<li>Total time of flight: {duration_mins} minutes and {duration_secs} seconds</li>'
    flight_info += f'<li>Maximum altitude gained: {peak:.2f} km</li>'
    flight_info += f'<li>Maximum horizontal distance travelled: {edge:.2f} km</li>'
    flight_info += f'<li>Total length of the trajectory: {length:.2f} km</li>'
    flight_info += '</ul>'
    response += flight_info

    # Visualization Task 3
    plt.figure(figsize=(10, 6))
    plt.xlim((data[:X,0]/1000).min() * 1, (data[:X,0]/1000).max() * 1.1)
    plt.ylim((data[:X,1]/1000).min() * 1, (data[:X,1]/1000).max() * 1.1)
    plt.title('Displacement graph of Y vs X', fontweight='bold')
    plt.xlabel('X Displacement (km)')
    plt.ylabel('Y Displacement (km)')
    plt.plot(data[:X,0]/1000, data[:X,1]/1000, color='black', linewidth=3.5)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    plot_url_1 = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('utf-8')
    response += f'<h2>Displacement Graph</h2><img src="{plot_url_1}">'

    # Visualization Task 4
    plt.figure(figsize=(10, 6))

    # X Displacement vs Time (TOP LEFT)
    plt.subplot(3,2,1)
    plt.xlim((data[:X,13]).min() * 1, (data[:X,13]).max() * 1.1)
    plt.ylim((data[:X,0]/1000).min() * 1, (data[:X,0]/1000).max() * 1.1)
    plt.title('X Displacement vs Time', fontweight='bold')
    plt.xlabel('Time elapsed (s)')
    plt.ylabel('X Displacement (km)')
    plt.plot(data[:X,13],data[:X,0]/1000)

    # Y Displacement vs Time (TOP RIGHT)
    plt.subplot(3,2,2)
    plt.xlim((data[:X,13]).min() * 1, (data[:X,13]).max() * 1.1)
    plt.ylim((data[:X,1]/1000).min() * 1, (data[:X,1]/1000).max() * 1.1)
    plt.title('Y Displacement vs Time', fontweight='bold')
    plt.xlabel('Time elapsed (s)')
    plt.ylabel('Y Displacement (km)')
    plt.plot(data[:X,13],data[:X,1]/1000, color='orange')

    # Total mass vs Time (MIDDLE LEFT)
    plt.subplot(3,2,3)
    A = np.arange(10000,210001,40000)
    plt.yticks(A)
    plt.xlim((data[:X,13]).min() * 1, (data[:X,13]).max() * 1.1)
    plt.ylim((data[:X,5]).min() * 1, (data[:X,5]).max() * 1.1)
    plt.title('Total mass (rocket + propellant) vs Time', fontweight='bold')
    plt.xlabel('Time elapsed (s)')
    plt.ylabel('Mass (kg)')
    plt.plot(data[:X,13],data[:X,5], color='crimson')

    # X Velocity/Y Velocity vs Time (MIDDLE RIGHT)
    plt.subplot(3,2,4)
    plt.xlim((data[:X,13]).min() * 1, (data[:X,13]).max() * 1.1)
    plt.ylim((data[:X,2]).min() * 1.1, (data[:X,2]).max() * 1.1)
    plt.title('X and Y Velocities vs Time', fontweight='bold')
    plt.xlabel('Time elapsed (s)')
    plt.ylabel('Velocity (m/s)')
    plt.plot(data[:X,13],data[:X,2], color='darkblue', label='Vx (m/s)')
    plt.plot(data[:X,13],data[:X,3], color='green', label='Vy (m/s)')
    plt.legend(loc='best', prop={'size': 8})

    # X Acceleration/Y Acceleration vs Time (BOTTOM LEFT)
    plt.subplot(3,2,5)
    plt.xlim((data[:X,13]).min() * 1, (data[:X,13]).max() * 1.1)
    plt.ylim((data[:X,14]).min() * 1.1, (data[:X,14]).max() * 1.1)
    plt.title('X and Y Accelerations vs Time', fontweight='bold')
    plt.xlabel('Time elapsed (s)')
    plt.ylabel('Acceleration (m/s²)')
    plt.plot(data[:X,13],data[:X,14], color='blue', label='Ax (m/s²)')
    plt.plot(data[:X,13],data[:X,15], color='orange', label='Ay (m/s²)')
    plt.legend(loc='best', prop={'size': 8})

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    plot_url_2 = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('utf-8')
    response += f'<h2>Time Series Graphs</h2><img src="{plot_url_2}">'

    return Response(response, mimetype='text/html')

if __name__ == '__main__':
    application.run(debug=True)
