import os
import sys
import platform
import socket
import hashlib
import datetime
import io
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from flask import Flask, Response
import base64

# Initialize Flask application
application = Flask(__name__)

@application.route('/')
def home():
    try:
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

        # Vortex simulation
        plt.rcParams['text.usetex'] = False  # Disable LaTeX rendering
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.size'] = 14

        no = 3
        circulations = np.array([1, 1/2, -1/3])

        def vortex_ode(t, y):
            epsilon = 1e-8  # Small regularization term to prevent division by zero
            dydt = []
            for i in range(no):
                xi = y[2 * i]
                yi = y[2 * i + 1]
                sum_x = 0
                sum_y = 0
                for j in range(no):
                    if i != j:
                        xj = y[2 * j]
                        yj = y[2 * j + 1]
                        common_denominator = (xi - xj) ** 2 + (yi - yj) ** 2 + epsilon
                        sum_x += (circulations[j] / (2 * np.pi)) * ((xi - xj) / common_denominator)
                        sum_y += (circulations[j] / (2 * np.pi)) * ((yi - yj) / common_denominator)
                dydt.append(sum_y)
                dydt.append(-sum_x)
            return dydt

        initial_conditions = np.array([-np.sqrt(3)+6*np.sqrt(3)*(1/7),0+6*np.sqrt(3)*(1/7),0+6*np.sqrt(3)*(1/7),0+(2/7),0+(2/7),1+(2/7)])

        t_span = (0, 1000)
        t_eval = np.linspace(t_span[0], t_span[1], 1000)

        solution = solve_ivp(vortex_ode, t_span, initial_conditions, t_eval=t_eval)

        x_sol = solution.y[::2]
        y_sol = solution.y[1::2]

        max_abs_x = np.max(np.abs(x_sol))
        max_abs_y = np.max(np.abs(y_sol))
        final_positions = solution.y[:, -1].reshape(2, no)
        max_circulation_x = np.max(np.abs(final_positions[0]))
        max_circulation_y = np.max(np.abs(final_positions[1]))
        max_lim_x = max(max_circulation_x, max_abs_x) * 1.25
        max_lim_y = max(max_circulation_y, max_abs_y) * 1.25

        fig, ax = plt.subplots(figsize=(10, 10), dpi=120)
        for i in range(no):
            ax.plot(x_sol[i], y_sol[i], label=f'Vortex {i + 1}')
            ax.plot(x_sol[i, 0], y_sol[i, 0], 'o')
            ax.arrow(x_sol[i, -2], y_sol[i, -2], x_sol[i, -1] - x_sol[i, -2], y_sol[i, -1] - y_sol[i, -2],
                     head_width=0.2, head_length=0.2, fc='k', ec='k', zorder=3)

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Trajectories of Vortices', fontsize=20)
        ax.set_xlim(min(0, min(np.min(final_positions[0]), np.min(x_sol))) * 1.25, max_lim_x)
        ax.set_ylim(min(0, min(np.min(final_positions[1]), np.min(y_sol))) * 1.25, max_lim_y)
        ax.set_aspect('equal', adjustable='box')

        ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
        ax.axvline(0, color='k', linestyle='--', linewidth=0.5)

        # Calculate circulation center only if circulation strengths are not all zero
        if np.sum(circulations) != 0:
            circulation_center = np.average(final_positions, axis=1, weights=circulations)
            ax.plot(circulation_center[0], circulation_center[1], 'ro', label='Eye of the Storm')
            ax.annotate(f'Eye of the Storm: ({circulation_center[0]:.2f}, {circulation_center[1]:.2f})',
                        xy=(circulation_center[0], circulation_center[1]), xycoords='data',
                        xytext=(-50, 50), textcoords='offset points',
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
        else:
            circulation_center = None

        # If circulation center is calculated, compute dispersion
        if circulation_center is not None:
            dispersion = np.mean(np.sqrt(np.sum((final_positions - circulation_center[:, np.newaxis]) ** 2, axis=0)))
            ax.text(-max_lim_x * 0.9, max_lim_y * 0.9, f'Dispersion: {dispersion:.4f}', fontsize=12)

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc='upper right')

        ax.grid(True)

        # Save the plot to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        plot_url = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('utf-8')
        response += f'<h2>Vortex Simulation</h2><img src="{plot_url}">'

        return Response(response, mimetype='text/html')
    
    except Exception as e:
        return Response(f"<h1>Internal Server Error</h1><p>{str(e)}</p>", mimetype='text/html')

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
