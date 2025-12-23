from flask import Flask, render_template_string, request, jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os
import requests
import json
from urllib.parse import quote
import pandas as pd

# Load client portfolio data
df = pd.read_csv('client_portfolio_data.csv')
last_row = json.loads(df.tail(1).to_json(orient='records'))[0]
client_details = json.dumps(last_row)
encoded_client_details = quote(client_details)

app = Flask(__name__)

# 🔹 Hardcoded dropdown list of client IDs
CLIENT_IDS = ["CL100000","CL100001","CL100002","CL100003","CL100004"
]

# 📊 Generate pie chart from allocation data
def generate_pie_chart(asset_allocation):
    
    labels = list(asset_allocation.keys())
    sizes = list(asset_allocation.values())

    plt.figure(figsize=(4, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%',labeldistance=1.1,     # Move labels slightly outward
    pctdistance=0.8 )
    plt.title("Asset Allocation")
    plt.tight_layout()
    os.makedirs("static", exist_ok=True)
    plt.savefig("static/asset_allocation.png")
    plt.close()

# 🔹 Client Details API route (mocked for now)
@app.route("/api/client/<client_id>")
def get_client_details(client_id):
    mock_data = {
        "C001": {
            "name": "Neha Sharma",
            "risk_profile": "Moderate",
            "net_worth": "₹2.5 Cr",
            "investment_goal": "Retirement in 15 years",
            "asset_allocation": {"Equity": 50, "Fixed Income": 30, "Real Estate": 10, "Cash": 10}
        },
        "C002": {
            "name": "Ravi Kumar",
            "risk_profile": "Aggressive",
            "net_worth": "₹4 Cr",
            "investment_goal": "Wealth growth in 10 years",
            "asset_allocation": {"Equity": 70, "Fixed Income": 20, "Gold": 5, "Cash": 5}
        },
        "C003": {
            "name": "Ananya Verma",
            "risk_profile": "Conservative",
            "net_worth": "₹1.2 Cr",
            "investment_goal": "Child education in 8 years",
            "asset_allocation": {"Equity": 30, "Fixed Income": 50, "Gold": 10, "Cash": 10}
        },
        "C004": {
            "name": "Amit Patel",
            "risk_profile": "Moderate",
            "net_worth": "₹3 Cr",
            "investment_goal": "Retirement in 20 years",
            "asset_allocation": {"Equity": 55, "Fixed Income": 25, "Real Estate": 10, "Cash": 10}
        },
        "C005": {
            "name": "Priya Iyer",
            "risk_profile": "Aggressive",
            "net_worth": "₹5 Cr",
            "investment_goal": "Global investment diversification",
            "asset_allocation": {"Equity": 65, "Fixed Income": 15, "Gold": 10, "Cash": 10}
        }
    }

   # client_data = mock_data.get(client_id)
   # if client_data:
     #   generate_pie_chart(client_data["asset_allocation"])
       # return jsonify(client_data)
   # else:
     #   return jsonify({"error": "Client not found"}), 404
        
    try:
        API_URL = f"https://p3whwikcjg.execute-api.us-east-1.amazonaws.com/getClientDetails?client_id={client_id}"
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        portfolio = {
        "Equities": data.get("equities_percentage", 0),
        "Bonds": data.get("bonds_percentage", 0),
        "Cash": data.get("cash_percentage", 0),
        "Alternatives": data.get("alternatives_percentage", 0),
        "Real Estate": data.get("real_estate_percentage", 0),
        "Commodities": data.get("commodities_percentage", 0),
        }
        generate_pie_chart(portfolio)
        return data
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Insights API route
@app.route("/api/insights", methods=["POST"])
def get_insights():
    client_details = request.json
    print("From Insights")
    print(client_details)
    encoded_details = quote(json.dumps(client_details))

    try:
        API_URL = f"https://im9cd3y00h.execute-api.us-east-1.amazonaws.com/generatePersonalisedInsights?client_details={encoded_details}"
        print(API_URL)
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Main UI
@app.route("/")
def index():
    return render_template_string("""
    <html>
    <head>
        <title>Client Portfolio & Insights</title>
        <style>
            body { font-family: Arial; margin: 20px; }
            .container { display: flex; gap: 20px;  height: 100vh; align-items: stretch;  }
            .left { flex: 1; }
            .right { flex: 2; }
            .card { padding: 10px; border: 1px solid #ccc; border-radius: 8px; margin-bottom: 15px; }
            .pie-card {padding: 2px; border: 1px solid #ccc; border-radius: 8px; margin-bottom: 15px;}
            .pie-card img {
        display: block;
        margin: 0 auto;
        max-width: 100%;
        height: auto;
    }
            img { max-width: 100%; }
            .insight-card { background: #f9f9f9; margin-bottom: 10px; padding: 10px; border-radius: 6px; }
            #loader { font-size: 18px; font-weight: bold; color: blue; }
            .insight-card h3 {
    margin: 0 0 4px;
    font-size: 16px;   /* was 16px */
    color: #333;
}
.insight-card p {
    margin: 0;
    font-size: 14px;   /* was 14px */
    color: #555;
    line-height: 1.3;  /* tighter line spacing */
}
        </style>
    </head>
    <body>
        <h1>Client Portfolio & Insights</h1>

        <label><strong>Select Client ID:</strong></label>
        <select id="clientSelect">
            <option value="">-- Select --</option>
            {% for cid in client_ids %}
                <option value="{{ cid }}">{{ cid }}</option>
            {% endfor %}
        </select>

        <br><br><br>
        <div id="loader" style="display:none;">Loading data...</div>

        <div class="container" id="portfolio" style="display:none;">
            <div class="left">
                <div class="card">
                    <h2>Client Details</h2>
                    <p><strong>Name:</strong> <span id="name"></span></p>
                    <p><strong>Risk Profile:</strong> <span id="risk_profile"></span></p>
                    <p><strong>Net Worth:</strong> <span id="net_worth"></span></p>
                    <p><strong>Investment Horizon:</strong> <span id="goal"></span></p>
                </div>

                <div class="pie-card">
                    <img id="allocation_img" src="" alt="Asset Allocation">
                </div>
            </div>

            <div class="right">
            <div class="card">
                <h2>Personalized Insights</h2>
                <div id="insights"></div>
                </div>
            </div>
        </div>

        <script>
            function updatePieChart() {
                const timestamp = new Date().getTime(); 
                document.getElementById('allocation_img').src = `/static/asset_allocation.png?${timestamp}`;
            }

            function renderInsights(insights) {
                let insightsDiv = document.getElementById("insights");
                insightsDiv.innerHTML = "";
                if (Array.isArray(insights)) {
                    insights.forEach(text => {
                        let div = document.createElement("div");
                        div.className = "insight-card";
                        const title = document.createElement('h3');
                        title.textContent = text.title;

                        const desc = document.createElement('p');
                        desc.textContent = text.desc;

                        div.appendChild(title);
                        div.appendChild(desc);
                        insightsDiv.appendChild(div);
                    });
                } else {
                    let div = document.createElement("div");
                    div.className = "insight-card";
                    div.textContent = JSON.stringify(insights);
                    insightsDiv.appendChild(div);
                }
            }

            document.getElementById("clientSelect").addEventListener("change", function() {
                let clientId = this.value;
                if (!clientId) return;

                document.getElementById("loader").style.display = "block";
                document.getElementById("portfolio").style.display = "none";

                // Step 1: Fetch Client Details
                fetch("/api/client/" + clientId)
                    .then(res => res.json())
                    .then(client => {
                        if (client.error) throw client.error;

                        // Fill in client details
                        document.getElementById("name").textContent = client.name;
                        document.getElementById("risk_profile").textContent = client.risk_appetite_label;
                        document.getElementById("net_worth").textContent = client.total_portfolio_value;
                        document.getElementById("goal").textContent = client.investment_horizon;
                        updatePieChart();

                        // Step 2: Fetch Insights
                        return fetch("/api/insights", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify(client)
                        });
                    })
                    .then(res => res.json())
                    .then(insights => {
                        renderInsights(insights);
                        document.getElementById("loader").style.display = "none";
                        document.getElementById("portfolio").style.display = "flex";
                    })
                    .catch(err => {
                        document.getElementById("portfolio").style.display = "flex";
                        document.getElementById("loader").textContent = "Error: " + err;
                    });
            });
        </script>
    </body>
    </html>
    """, client_ids=CLIENT_IDS)

if __name__ == "__main__":
    app.run(debug=True)
