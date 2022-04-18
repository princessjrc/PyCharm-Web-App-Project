from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, DecimalField
import requests
# dnspython

app = Flask(__name__)

app.config["SECRET_KEY"] = "vanillaicecreampopsugar"
app.config["MONGO_URI"] = "mongodb+srv://jcamp201:fivesos@cluster0.m5tjv.mongodb.net/db?retryWrites=true&w=majority"
mongo = PyMongo(app)

class Expenses(FlaskForm):
    description = StringField('Description')
    category = SelectField('Category',
                       choices=[('rent', 'Rent'),
                                ('groceries', 'Groceries'),
                                ('insurance', 'Insurance'),
                                ('gas', 'Gas'),
                                ('college', 'College'),
                                ('water', 'Water'),
                                ('electricity', 'Electricity'),
                                ('mortgage', 'Mortgage')
                                ])
    cost = DecimalField('Cost')
    currency = SelectField('Currency',
                           choices=[('USDUSD', 'United States Dollar'),
                                    ('USDCOP', 'Colombian Peso'),
                                    ('USDBRL', 'Brazilian Real'),
                                    ('USDCAD', 'Canadian Dollar'),
                                    ('USDRUB', 'Russian Ruble'),
                                    ('USDNZD', 'New Zealand Dollar'),
                                    ('USDMXN', 'Mexican Peso'),
                                    ('USDGBP', 'British Pound Sterling'),
                                    ('USDAUD', 'Australian Dollar'),
                                    ('USDEUR', 'Euro')
                           ])
    date = DateField(format='%Y-%m-%d')

def get_total_expenses(category):
    total_category = mongo.db.expenses.find({"category": category})
    category_cost = 0
    for i in total_category:
        category_cost += float(i["cost"])
    format_cost = "{:.2f}".format(category_cost)

    return format_cost

@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    total_cost = 0

    for i in my_expenses:
        total_cost += float(i["cost"])
    total_cost = "{:.2f}".format(total_cost)

    expensesByCategory = [
        ("rent", get_total_expenses("rent")),
        ("groceries", get_total_expenses("groceries")),
        ("insurance", get_total_expenses("insurance")),
        ("gas", get_total_expenses("gas")),
        ("college", get_total_expenses("college")),
        ("water", get_total_expenses("water")),
        ("electricity", get_total_expenses("electricity")),
        ("mortgage", get_total_expenses("mortgage"))
    ]

    return render_template("index.html", expenses=total_cost, expensesByCategory=expensesByCategory)

@app.route('/addExpenses', methods=["GET","POST"])
def addExpenses():
    expensesForm = Expenses(request.form)
    if request.method == "POST":
        description_entered = request.form['description']
        category_entered = request.form['category']
        cost_entered = float(request.form['cost'])
        currency_entered = request.form['currency']
        date_entered = request.form['date']

        cost_entered = currency_converter(cost_entered, currency_entered)

        expense = {"description": description_entered, "category": category_entered,
                   "cost": cost_entered, "currency": currency_entered, "date": date_entered}

        mongo.db.expenses.insert_one(expense)
        return render_template("expenseAdded.html")
    return render_template("addExpenses.html", form=expensesForm)

def currency_converter(cost,currency):
    url="http://api.currencylayer.com/live?access_key=eadfaf31aa7aa3e362230fa7f23f4724"
    response = requests.get(url).json()
    rate = response["quotes"][currency]
    converted_cost = cost / rate
    return converted_cost

app.run(debug=True, port=8000)
