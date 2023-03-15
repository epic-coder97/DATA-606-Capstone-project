from flask import Flask, render_template, request
#import openai_secret_manager
import openai
import os

app = Flask(__name__)

# Load OpenAI API credentials
#secrets = openai_secret_manager.get_secret("openai")
api_key =  # enter the API key
openai.api_key = api_key


@app.route("/")
def index():
    return render_template("Home.html")


@app.route("/itinerary", methods=["POST"])
def generate_itinerary():
    start_dest = request.form["start"]
    final_dest = request.form["end"]
    num_days = request.form["days"]

    # Generate travel itinerary using ChatGPT API
    model_engine = "text-davinci-003"
    prompt = f"Generate a detailed {num_days}-day itinerary from {start_dest} to {final_dest} and also places to visit in {final_dest}"
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    print(type(response))
    itinerary = response.choices[0].text.strip()
    itinerary = itinerary.replace("\n", "<br>")
    print(type(itinerary))



    return render_template("itinerary.html", itinerary=itinerary)


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 8080)))
