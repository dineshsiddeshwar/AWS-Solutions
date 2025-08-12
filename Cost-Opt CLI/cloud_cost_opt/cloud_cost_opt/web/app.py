from flask import Flask, render_template, request, redirect, url_for, flash
import subprocess
from cloud_cost_opt.services import list_services
from cloud_cost_opt.recommend import get_recommendation

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def home():
    services = list_services()
    return render_template('home.html', services=services)

@app.route('/recommend/<service>')
def recommend(service):
    recs = get_recommendation(service)
    return render_template('recommend.html', service=service, recommendations=recs)

@app.route('/remediate/<service>/<int:index>', methods=['POST'])
def remediate(service, index):
    # Call CLI for remediation
    result = subprocess.run([
        'python', '-m', 'cloud_cost_opt.cli', 'remediate', service, str(index), '--auto'
    ], capture_output=True, text=True)
    output = result.stdout + '\n' + result.stderr
    flash(output)
    return redirect(url_for('recommend', service=service))

if __name__ == '__main__':
    app.run(debug=True,port=5555)
