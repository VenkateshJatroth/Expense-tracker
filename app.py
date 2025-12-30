from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'category': self.category,
            'amount': self.amount,
            'description': self.description
        }

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_expense', methods=['POST'])
def add_expense():
    try:
        date_str = request.form.get('date')
        category = request.form.get('category')
        amount = float(request.form.get('amount'))
        description = request.form.get('description', '')
        
        expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        new_expense = Expense(
            date=expense_date,
            category=category,
            amount=amount,
            description=description
        )
        
        db.session.add(new_expense)
        db.session.commit()
        
        return redirect(url_for('index'))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/get_expenses')
def get_expenses():
    expenses = Expense.query.order_by(Expense.date.desc()).limit(10).all()
    return jsonify([expense.to_dict() for expense in expenses])

@app.route('/get_stats')
def get_stats():
    expenses = Expense.query.all()
    
    total_spent = sum(expense.amount for expense in expenses)
    
    # Calculate expenses by category
    category_totals = {}
    for expense in expenses:
        if expense.category in category_totals:
            category_totals[expense.category] += expense.amount
        else:
            category_totals[expense.category] = expense.amount
    
    return jsonify({
        'total_spent': round(total_spent, 2),
        'category_totals': category_totals
    })

@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        expense = Expense.query.get_or_404(expense_id)
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
