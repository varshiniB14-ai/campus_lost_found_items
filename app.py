from flask import Flask, render_template, request, redirect, url_for
from bson.objectid import ObjectId
from datetime import datetime
from db_config import lost_items, found_items, alerts

app = Flask(__name__)

# --- HOME ---
@app.route('/')
def index():
    return render_template('index.html')

# --- LOST ITEMS ---
@app.route('/report_lost', methods=['GET', 'POST'])
def report_lost():
    if request.method == 'POST':
        item = {
            "item_name": request.form.get('item_name'),
            "category": request.form.get('category'),
            "description": request.form.get('description'),
            "location": request.form.get('location'),
            "date_lost": request.form.get('date_lost'),
            "reported_by": request.form.get('reported_by'),
            "contact": request.form.get('contact'),
            "status": "Lost",  # Default status
            "created_at": datetime.now()
        }
        lost_items.insert_one(item)
        return redirect(url_for('view_lost'))
    return render_template('report_lost.html')

@app.route('/lost_items')
def view_lost():
    items = list(lost_items.find().sort("created_at", -1))
    return render_template('lost_items.html', items=items)

# NEW: Update status to Found
@app.route('/mark_found/<id>')
def mark_found(id):
    lost_items.update_one(
        {"_id": ObjectId(id)}, 
        {"$set": {"status": "Found/Resolved"}}
    )
    return redirect(url_for('view_lost'))

# --- FOUND ITEMS ---
@app.route('/report_found', methods=['GET', 'POST'])
def report_found():
    if request.method == 'POST':
        found_data = {
            "item_name": request.form.get('item_name'),
            "category": request.form.get('category'),
            "description": request.form.get('description'),
            "location_found": request.form.get('location_found'),
            "date_found": request.form.get('date_found'),
            "found_by": request.form.get('found_by'),
            "contact": request.form.get('contact'),
            "created_at": datetime.now()
        }
        result = found_items.insert_one(found_data)
        found_id = result.inserted_id

        # Matching Logic
        match = lost_items.find_one({
            "item_name": {"$regex": found_data['item_name'], "$options": "i"},
            "category": found_data['category'],
            "status": "Lost" # Only match items still marked as Lost
        })

        if match:
            alert_doc = {
                "lost_item_id": match['_id'],
                "found_item_id": found_id,
                "item_name": found_data['item_name'],
                "message": f"A matching '{found_data['item_name']}' was found!",
                "status": "unread",
                "created_at": datetime.now()
            }
            alerts.insert_one(alert_doc)

        return redirect(url_for('view_found'))
    return render_template('report_found.html')

@app.route('/found_items')
def view_found():
    items = list(found_items.find().sort("created_at", -1))
    return render_template('found_items.html', items=items)

# --- ALERTS & DELETES ---
@app.route('/alerts')
def view_alerts():
    all_alerts = list(alerts.find().sort("created_at", -1))
    return render_template('alerts.html', alerts=all_alerts)

@app.route('/mark_read/<id>')
def mark_read(id):
    alerts.update_one({"_id": ObjectId(id)}, {"$set": {"status": "read"}})
    return redirect(url_for('view_alerts'))

@app.route('/delete_lost/<id>')
def delete_lost(id):
    lost_items.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('view_lost'))

@app.route('/delete_found/<id>')
def delete_found(id):
    found_items.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('view_found'))

@app.route('/delete_alert/<id>')
def delete_alert(id):
    alerts.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('view_alerts'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)