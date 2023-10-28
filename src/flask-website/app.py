from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global variable to store existing event types
existing_event_types = []

# Existing route


@app.route('/')
def index():
    return render_template('index.html')

# New route for Manage Event Types


@app.route('/manage_event_types', methods=['GET', 'POST'])
def manage_event_types():
    if request.method == 'POST':
        new_type = request.form.get('newTypeName')
        if new_type:
            existing_event_types.append(new_type)

    return render_template('manage_event_types.html', existing_event_types=existing_event_types)

# New route to handle updates from the frontend


@app.route('/update_event_types', methods=['POST'])
def update_event_types():
    action = request.form.get('action')
    type_name = request.form.get('typeName')

    if action == 'add':
        existing_event_types.append(type_name)
        return jsonify({'message': f'The type "{type_name}" has been added.'})
    elif action == 'delete':
        existing_event_types.remove(type_name)
        return jsonify({'message': f'The type "{type_name}" has been deleted.'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
