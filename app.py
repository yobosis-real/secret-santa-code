import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, make_response, render_template, send_file
import os
from dotenv import load_dotenv
import random
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO

load_dotenv()
sender = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')

def createpair(pair1):
    a = 1
    p1 = list(pair1.items())
    p2 = p1.copy()
    while a == 1:
        random.shuffle(p2)
        for i in range(len(p1)):
            if p1[i] != p2[i]:
                a = 0
            else:
                a = 1
                break
    return dict(p2)

def create_circular_graph(names, pairs):
    G = nx.DiGraph()
    p1= list(names.items())
    p2= list(pairs.items())
    # Add nodes and edges
    for i in range(len(p1)):
        G.add_edge(p1[i][0], p2[i][0])

    # Circular layout for the graph
    pos = nx.circular_layout(G)

    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold", 
            arrowsize=20, arrowstyle='-|>')
    plt.title("Secret Santa Pairings", fontsize=16)
    
    static_dir = os.path.join(os.getcwd(), 'static')
    os.makedirs(static_dir, exist_ok=True)  # Ensure the static directory exists
    output_path = os.path.join(static_dir, 'secret_santa_graph.png')

    plt.savefig(output_path)
    plt.close()

    return output_path

def send_email(price, p1, p2):
    pair1 = list(p1.items())
    pair2 = list(p2.items())
    for i in range(len(pair1)):
        subject = "Your Secret Santa Match is Here!"
        body = f"""Hi {pair1[i][0]},

        It's time for some holiday cheer! 
        I'm thrilled to let you know that you are the Secret Santa for {pair2[i][0]}! 

        Here are a few details about {pair2[i][0]}:
        Email: {pair2[i][1][0]}
        Address: {pair2[i][1][1]}

        Please remember, the maximum price for the gift is {price}. Let's keep it thoughtful and fun! 

        Happy gifting,
        Santa's Elf
        """
        msg = f"Subject:{subject}\n\n{body}"
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()

            server.login(sender, sender_password)

            server.sendmail(sender, pair1[i][1][0], msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            server.quit()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def getvalues():
    if request.method == 'POST':
        max_price = request.form['max_price']
        name = request.form.getlist('recipient_name')
        email = request.form.getlist('recipient_email')
        address= request.form.getlist('recipient_address')
        names = {k: (v1, v2) for k, v1, v2 in zip(name,email,address)}
        print(names)  
        pair = createpair(names)
        print(pair)
        graph_path = create_circular_graph(names, pair)  # Generate circular graph
        send_email(max_price, names, pair)
        return make_response(render_template('thank.html', graph_path=graph_path), 200)
    return make_response(render_template('index.html'), 200)

@app.route('/download_graph')
def download_graph():
    static_dir = os.path.join(os.getcwd(), 'static')
    file_path = os.path.join(static_dir, 'secret_santa_graph.png')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run()
