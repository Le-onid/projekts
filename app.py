from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def initialize_database():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            due_date DATE NOT NULL,
            priority TEXT CHECK(priority IN ('Extreme', 'High', 'Medium', 'Low'))
        )
    ''')
    conn.commit()
    conn.close()

initialize_database()

def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_all_tasks():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return tasks

def add_task(name, due_date, priority):
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (name, due_date, priority) VALUES (?, ?, ?)',
                 (name, due_date, priority))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def update_task(task_id, name, due_date, priority):
    conn = get_db_connection()
    conn.execute('''UPDATE tasks 
                    SET name = ?, due_date = ?, priority = ?
                    WHERE id = ?''',
                 (name, due_date, priority, task_id))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    tasks = get_all_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/manage', methods=['GET', 'POST'])
@app.route('/manage/<int:task_id>', methods=['GET', 'POST'])
def manage(task_id=None):
    if request.method == 'POST':
        name = request.form['name']
        due_date = request.form['due_date']
        priority = request.form['priority']
        
        if task_id:
            update_task(task_id, name, due_date, priority)
        else:
            add_task(name, due_date, priority)
            
        return redirect(url_for('index'))
    
    task = None
    if task_id:
        conn = get_db_connection()
        task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        conn.close()
    
    return render_template('manage.html', task=task)

@app.route('/delete/<int:task_id>')
def delete(task_id):
    delete_task(task_id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)