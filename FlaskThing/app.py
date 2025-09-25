from flask import Flask, render_template

#set the recusion limit higher
import sys
sys.setrecursionlimit(30000)
sys.set_int_max_str_digits(20000)

app = Flask(__name__) #this has 2 underscores on each side

@app.route('/')
def index():
        return render_template('index.html.j2', name="Kellen")

@app.route('/factorial')
def factorialPage():
    return render_template('factorial.html.j2', factorial=[factorial(i) for i in range(1,3000)])

def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)