from flask import Flask, request, jsonify
from importlib.resources import files
from hdd_lifetime_prediction import parse_smartctl, TreeModel, predict_lifetime, predict_full

app = Flask(__name__)

@app.route('/hdd-lifetime-prediction/', methods=['POST'])
def predict():
    smart_output = request.data.decode('utf-8')

    try:
        smart_attributes = parse_smartctl(smart_output)
        model = TreeModel(
            files('hdd_lifetime_prediction.model').joinpath("long-term-params.yaml")
        )
        predicted_lifetime = predict_lifetime(smart_attributes, model)
        prediction_stats = predict_full(smart_attributes, model)

        response = {
            "predicted_lifetime": predicted_lifetime,
            "predicted_stats": prediction_stats
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": e}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
