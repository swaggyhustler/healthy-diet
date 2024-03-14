from flask import Flask, render_template, request
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.chains import LLMChain
import os
import re
os.environ['OPENAI_API_KEY'] = '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' # your openai key
app = Flask(__name__)
llm_resto = OpenAI(temperature=0.6)
prompt_template_resto = PromptTemplate(
    input_variables=['age', 'gender', 'weight', 'height', 'veg_or_nonveg', 'disease', 'region', 'allergics', 'foodtype'],
    template="Diet Recommendation System:\n"
             "I want you to recommend 6 restaurants names, 6 breakfast names, 5 dinner names, and 6 workout names, "
             "based on the following criteria:\n"
             "Person age: {age}\n"
             "Person gender: {gender}\n"
             "Person weight: {weight}\n"
             "Person height: {height}\n"
             "Person veg_or_nonveg: {veg_or_nonveg}\n"
             "Person generic disease: {disease}\n"
             "Person region: {region}\n"
             "Person allergics: {allergics}\n"
             "Person foodtype: {foodtype}."
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    if request.method == "POST":
        age = request.form['age']
        gender = request.form['gender']
        weight = request.form['weight']
        height = request.form['height']
        veg_or_noveg = request.form['veg_or_nonveg']
        disease = request.form['disease']
        region = request.form['region']
        allergics = request.form['allergics']
        foodtype = request.form['foodtype']

        chain_resto = LLMChain(llm=llm_resto, prompt=prompt_template_resto)
        input_data = {'age': age,
                      'gender': gender,
                      'weight': weight,
                      'height': height,
                      'veg_or_nonveg': veg_or_noveg,
                      'disease': disease,
                      'region': region,
                      'allergics': allergics,
                      'foodtype': foodtype}
        results = chain_resto.invoke(input_data)
        if isinstance(results, dict):
            results_string = results.get('text', '')  # Assuming 'text' key contains the text output
        else:
            results_string = results

        # Extracting the different recommendations using regular expressions
        restaurant_names = re.findall(r'Restaurants:(.*?)Breakfast:', results_string, re.DOTALL)
        breakfast_names = re.findall(r'Breakfast:(.*?)Dinner:', results_string, re.DOTALL)
        dinner_names = re.findall(r'Dinner:(.*?)Workouts:', results_string, re.DOTALL)
        workout_names = re.findall(r'Workouts:(.*?)$', results_string, re.DOTALL)

        # Cleaning up the extracted lists and handling empty cases
        restaurant_names = [name.strip() for name in restaurant_names[0].strip().split('\n') if name.strip()] if restaurant_names else ['Sorry, No Restaurant Names!']
        breakfast_names = [name.strip() for name in breakfast_names[0].strip().split('\n') if name.strip()] if breakfast_names else ['Sorry, No Breakfast Names!']
        dinner_names = [name.strip() for name in dinner_names[0].strip().split('\n') if name.strip()] if dinner_names else ['Sorry, No Dinner Names!']
        workout_names = [name.strip() for name in workout_names[0].strip().split('\n') if name.strip()] if workout_names else ['Sorry, No Workout Names!']

        return render_template('result.html', restaurant_names=restaurant_names, breakfast_names=breakfast_names,
                               dinner_names=dinner_names, workout_names=workout_names, user_region=region)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
