from flask import Flask, render_template, request, redirect, url_for, flash
import cx_Oracle

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    dsn = cx_Oracle.makedsn('localhost', 1521, sid='xe')
    return cx_Oracle.connect(user='sys', password='1809', dsn=dsn, mode=cx_Oracle.SYSDBA)

@app.route('/')
def index():
    # You might want to pass in additional data to render on the homepage
    return render_template('index.html')

@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        name = request.form.get('name')
        contact = request.form.get('contact')
        city = request.form.get('city')
        
        if not all([supplier_id, name, contact, city]):
            flash('All fields are required.')
            return redirect(url_for('add_supplier'))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Convert supplier_id to int and ensure other data is properly escaped to prevent SQL injection
            cursor.execute('INSERT INTO Supplier (Supplier_ID, Name, Contact, City) VALUES (:1, :2, :3, :4)', 
                           (int(supplier_id), name, contact, city))
            conn.commit()
            flash('Supplier added successfully!')
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            if error.code == 1:
                flash('Supplier ID already exists.')
            else:
                flash('Database error: ' + str(error.code))
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))
    return render_template('add_supplier.html')

if __name__ == '__main__':
    app.run(debug=True)