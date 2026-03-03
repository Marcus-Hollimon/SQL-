import sqlite3
from datetime import datetime, date
from colorama import Fore, Style

# Initialize database connection and cursor
conn = sqlite3.connect("todo_list.db")
cursor = conn.cursor()

# Create the table if it doesn't exist
# Used 'due_date' as a single TEXT column in YYYY-MM-DD format for easy sorting
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    task_name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    date_added TEXT,
    due_date TEXT
);
''')

def add_task(task_name, description, year, month, day):
    """Formats inputs into a sortable date string and saves to the DB."""
    date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # .zfill(2) ensures months/days like '9' become '09' so they sort correctly
    due_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    cursor.execute('''INSERT INTO tasks (task_name, description, status, date_added, due_date)
                   VALUES (?,?, 'pending',?,?) ''', (task_name, description, date_added, due_date))
    conn.commit()
    print(Fore.GREEN + f"Task, '{task_name}', added successfully." + Style.RESET_ALL)

def view_tasks():
    """Retrieves tasks sorted by date and calculates time remaining for each."""
    # ORDER BY due_date ASC puts the closest deadlines at the top
    cursor.execute("SELECT * FROM tasks ORDER BY due_date ASC")
    tasks = cursor.fetchall()
    
    today = date.today()
    
    print("\nCurrent Tasks: (Sorted by Due Date)")
    for task in tasks:
        # Convert the stored string back into a date object to do math
        Due_Date_str = task[5]
        Due_date_obj = datetime.strptime(Due_Date_str, "%Y-%m-%d").date()
        
        # Calculate difference between the deadline and today
        Due_Date_Diff = Due_date_obj - today
        Days_Left = Due_Date_Diff.days
        
        # Displaying task details with the calculated days remaining
        print(Fore.CYAN + f"ID: {task[0]} | Name: {task[1]} | Status: {task[3]} | "
              f"Added: {task[4]} | Due: {task[5]} | Days Left: {Days_Left}" + Style.RESET_ALL)

def update_task_status(task_id, new_status):
    """Updates the status (pending, in-progress, complete) for a specific task ID."""
    cursor.execute('UPDATE tasks SET status = ? WHERE id= ?', (new_status, task_id))
    conn.commit()
    print(Fore.YELLOW + f"Task ID {task_id} updated to '{new_status}'." + Style.RESET_ALL)

def delete_task(task_id):
    """Permanently removes a task from the database by its ID."""
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,)) 
    conn.commit()
    print(Fore.RED + f"Task ID {task_id} deleted." + Style.RESET_ALL) 

# --- Main Application Loop ---
while True:
    print("\nOptions: 1) Add Task 2) View Tasks 3) Update Task 4) Delete Task 5) Exit")
    choice = input("Choose an option: ")

    if choice == '1':
        task_name = input("Enter task name: ")
        description = input("Enter task description: ")
        year = input("Enter the year it's due (YYYY): ")
        month = input("Enter the month it's due (MM): ")
        day = input("Enter the day it's due (DD): ")
        add_task(task_name, description, year, month, day)

    elif choice == '2':
        view_tasks()

    elif choice == '3':
        task_id = input("Enter the ID of the task to update: ")
        new_status = input("Enter new status (pending, in-progress, complete): ")
        update_task_status(task_id, new_status)

    elif choice == '4':
        task_id = input("Enter the ID of the task to delete: ")
        delete_task(task_id)

    elif choice == '5':
        print("Closing application...")
        break

    else:
        print("Invalid option. Please try again.")

# Close connection before exiting
conn.close()
