import pandas as pd
import pandera.pandas as pa 
from flask import Flask, request, jsonify

from data_contract import SensorData 

app = Flask(__name__)

@app.route("/data/power", methods=["POST"])

# data validation process
def validate():
  data = request.get_json()
  print(f"\n[sever] Data: {data}")

  df = pd.DataFrame([data])

  try:
    SensorData.validate(df)
    print("✅ [Server] Data is valid and accepted.")
    return jsonify({"status": "success"}), 200
  except pa.errors.SchemaError as e:
    print("❌ [Server] INVALID DATA! Rejected.")
    error_report = e.failure_cases.to_dict()
    print(f"Report: {error_report}")
    return jsonify({
        "status" : "error",
        "error_details" : error_report
    }), 400
    
# Starting the Server
if __name__ == "__main__":
  print("[Server] Flask server is starting on port 5001...")
  app.run(port=5001)
