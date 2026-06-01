from flask import Flask, render_template, request, redirect

app = Flask(__name__)

contacts = []


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/alert')
def alert_page():
    return render_template(
        "alert.html",
        contacts=contacts
    )


@app.route('/contacts', methods=['GET', 'POST'])
def contacts_page():

    message = ""

    if request.method == 'POST':

        name = request.form['name']
        phone = request.form['phone']

        contacts.append({
            'name': name,
            'phone': phone
        })

        message = "Contact Saved Successfully!"

    return render_template(
        "contacts.html",
        contacts=contacts,
        count=len(contacts),
        message=message
    )


@app.route('/delete/<int:index>')
def delete_contact(index):

    if 0 <= index < len(contacts):
        contacts.pop(index)

    return redirect('/contacts')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
