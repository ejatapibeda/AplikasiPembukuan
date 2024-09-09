import sqlite3
from datetime import datetime
from error_handling import setup_error_handling
import os
import shutil
import uuid

COLUMN_MAPPINGS = {
    'consumers': {
        'Tanggal': 'date',
        'Nama Konsumen': 'name',
        'Alamat': 'address',
        'Sales': 'sales',
        'Pekerjaan': 'job',
        'Total Proyek': 'total_projects',
        'Tukang': 'worker',
        'Keterangan': 'notes'
    },
    'sales_projects': {
        'Nama Konsumen': 'customer_name',
        'Alamat': 'address',
        'Pekerjaan': 'job',
        'Total Proyek': 'total_project',
        'Komisi': 'commission',
        'KB': 'kb',
        'Keterangan': 'notes'
    },
    'worker_projects': {
        'Nama Konsumen': 'customer_name',
        'Alamat': 'address',
        'Pekerjaan': 'job',
        'Ukuran': 'size',
        'KB': 'kb',
        'Keterangan': 'notes'
    }
}

class DatabaseManager:
    def __init__(self, db_name='project_management.db'):
        setup_error_handling()
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.check_and_update_closed_books()
        self.check_and_update_closed_books_photo()
        self.migrate_materials_usage_table()


    def check_and_update_closed_books_photo(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE 'sales_projects_backup_%' OR name LIKE 'worker_projects_backup_%')")
        closed_books = self.cursor.fetchall()

        for book in closed_books:
            book_name = book[0]
            if not self.column_exists(book_name, 'photo_path'):
                self.cursor.execute(f"ALTER TABLE {book_name} ADD COLUMN photo_path TEXT")
    
        self.conn.commit()
    
    def check_and_update_closed_books(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'consumers_backup_%'")
        closed_books = self.cursor.fetchall()

        for book in closed_books:
            book_name = book[0]
            if not self.column_exists(book_name, 'date'):
                self.cursor.execute(f"ALTER TABLE {book_name} ADD COLUMN date TEXT DEFAULT ''")
                temp_table_name = f"{book_name}_temp"
                self.cursor.execute(f'''
                CREATE TABLE {temp_table_name} (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    name TEXT,
                    address TEXT,
                    sales TEXT,
                    job TEXT,
                    total_projects TEXT,
                    worker TEXT,
                    notes TEXT,
                    year INTEGER,
                    month INTEGER,
                    user_id INTEGER
                )
                ''')

                self.cursor.execute(f'''
                INSERT INTO {temp_table_name} (id, date, name, address, sales, job, total_projects, worker, notes, year, month, user_id)
                SELECT id, date, name, address, sales, job, total_projects, worker, notes, year, month, user_id FROM {book_name}
                ''')
                self.cursor.execute(f"DROP TABLE {book_name}")
                self.cursor.execute(f"ALTER TABLE {temp_table_name} RENAME TO {book_name}")

        self.conn.commit()

    def column_exists(self, table_name, column_name):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in self.cursor.fetchall()]
        return column_name in columns

    def create_tables(self):
        # Consumers table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS consumers (
            id INTEGER PRIMARY KEY,
            date TEXT,
            name TEXT,
            address TEXT,
            sales TEXT,
            job TEXT,
            total_projects TEXT,
            worker TEXT,
            notes TEXT,
            year INTEGER,
            month INTEGER,
            user_id INTEGER
        )
        ''')

        # Sales table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            name TEXT,
            user_id INTEGER
        )
        ''')

        # Update sales_projects table to include sales_id and user_id
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_projects (
            id INTEGER PRIMARY KEY,
            sales_id INTEGER,
            customer_name TEXT,
            address TEXT,
            job TEXT,
            total_project TEXT,
            commission TEXT,
            kb TEXT,
            notes TEXT,
            year INTEGER,
            month INTEGER,
            user_id INTEGER,
            photo_path TEXT,
            FOREIGN KEY (sales_id) REFERENCES sales (id)
        )
        ''')

        # Tukang table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tukang (
            id INTEGER PRIMARY KEY,
            name TEXT,
            user_id INTEGER
        )
        ''')

        # Update worker_projects table to include tukang_id and user_id
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS worker_projects (
            id INTEGER PRIMARY KEY,
            tukang_id INTEGER,
            customer_name TEXT,
            address TEXT,
            job TEXT,
            size TEXT,
            kb TEXT,
            notes TEXT,
            year INTEGER,
            month INTEGER,
            user_id INTEGER,
            photo_path TEXT,
            FOREIGN KEY (tukang_id) REFERENCES tukang (id)
        )
        ''')

        # Projects table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT,
            sales_name TEXT,
            worker_name TEXT,
            start_date TEXT,
            end_date TEXT,
            total_project TEXT,
            dp TEXT,
            user_id INTEGER
        )
        ''')

        # Materials usage table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials_usage (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            date TEXT,
            item_name TEXT,
            quantity TEXT,
            unit_price TEXT,
            total TEXT,
            notes TEXT,
            user_id INTEGER,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
        ''')

        if not self.column_exists('sales_projects', 'photo_path'):
           self.cursor.execute("ALTER TABLE sales_projects ADD COLUMN photo_path TEXT")
        
        if not self.column_exists('worker_projects', 'photo_path'):
              self.cursor.execute("ALTER TABLE worker_projects ADD COLUMN photo_path TEXT")
        
        # Periksa apakah kolom 'date' sudah ada
        if not self.column_exists('consumers', 'date'):
        # Tambahkan kolom 'date' tepat setelah kolom 'id'
            self.cursor.execute("ALTER TABLE consumers ADD COLUMN date TEXT DEFAULT ''")
            self.cursor.execute("UPDATE consumers SET date = (SELECT date FROM consumers AS temp WHERE temp.id = consumers.id) WHERE EXISTS (SELECT 1 FROM consumers AS temp WHERE temp.id = consumers.id)")
        
        # Buat tabel sementara dengan urutan kolom yang benar
            self.cursor.execute('''
            CREATE TABLE consumers_temp (
                id INTEGER PRIMARY KEY,
                date TEXT,
                name TEXT,
                address TEXT,
                sales TEXT,
                job TEXT,
                total_projects TEXT,
                worker TEXT,
                notes TEXT,
                year INTEGER,
                month INTEGER,
                user_id INTEGER
            )
            ''')

            self.cursor.execute('''
            INSERT INTO consumers_temp (id, date, name, address, sales, job, total_projects, worker, notes, year, month, user_id)
            SELECT id, date, name, address, sales, job, total_projects, worker, notes, year, month, user_id FROM consumers
            ''')
        
            self.cursor.execute("DROP TABLE consumers")

            self.cursor.execute("ALTER TABLE consumers_temp RENAME TO consumers")

            self.conn.commit()
    
    def migrate_materials_usage_table(self):
        self.cursor.execute("PRAGMA table_info(materials_usage)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        if 'unit_price' not in columns:
            self.cursor.execute("ALTER TABLE materials_usage ADD COLUMN unit_price TEXT")

            self.cursor.execute("UPDATE materials_usage SET unit_price = CAST(total AS REAL) / CAST(quantity AS REAL) WHERE quantity != '0' AND quantity != ''")
            
            self.conn.commit()

    def insert_consumer(self, data, year, month, user_id):
        self.cursor.execute('''
        INSERT INTO consumers (date, name, address, sales, job, total_projects, worker, notes, year, month, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*data, year, month, user_id))
        self.conn.commit()
        return self.cursor.lastrowid


    def insert_project(self, data, user_id):
        self.cursor.execute('''
        INSERT INTO projects (name, sales_name, worker_name, start_date, end_date, total_project, dp, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*data, user_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_material_usage(self, project_id, data, user_id):
        self.cursor.execute('''
        INSERT INTO materials_usage (project_id, date, item_name, quantity, unit_price, total, notes, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, *data, user_id))
        self.conn.commit()

    def get_consumers(self, year=None, month=None, user_id=None):
        query = "SELECT * FROM consumers WHERE user_id = ?"
        params = [user_id]
        if year is not None and month is not None:
            query += " AND year = ? AND month = ?"
            params.extend([year, month])
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_sales_projects(self, year=None, month=None, user_id=None):
        query = "SELECT * FROM sales_projects WHERE user_id = ?"
        params = [user_id]
        if year is not None and month is not None:
            query += " AND year = ? AND month = ?"
            params.extend([year, month])
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_worker_projects(self, tukang_id, user_id):
        self.cursor.execute('''
        SELECT id, customer_name, address, job, size, kb, notes 
        FROM worker_projects 
        WHERE tukang_id = ? AND user_id = ?
        ''', (tukang_id, user_id))
        return self.cursor.fetchall()

    def get_projects(self, user_id):
        self.cursor.execute("SELECT * FROM projects WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    def get_material_usage(self, project_id, user_id):
        self.cursor.execute("SELECT * FROM materials_usage WHERE project_id = ? AND user_id = ?", (project_id, user_id))
        return self.cursor.fetchall()
    
    def delete_record(self, table_name, record_id, user_id):
        self.cursor.execute(f"DELETE FROM {table_name} WHERE id = ? AND user_id = ?", (record_id, user_id))
        self.conn.commit()
    
    def close_book_for_person(self, table_name, person_id, user_id):
        current_date = datetime.now()
        year, month, day = current_date.year, current_date.month, current_date.day
    
        counter = 1
        while True:
            backup_table_name = f"{table_name}_backup_{person_id}_{user_id}_{year}_{month}_{day}_{counter}"
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (backup_table_name,))
            if not self.cursor.fetchone():
                break
            counter += 1

        # Buat backup tabel
        if table_name == 'sales_projects':
            self.cursor.execute(f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name} WHERE sales_id = ? AND user_id = ?", (person_id, user_id))
        elif table_name == 'worker_projects':
            self.cursor.execute(f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name} WHERE tukang_id = ? AND user_id = ?", (person_id, user_id))

        # Rename foto folder
        old_folder = f"foto/{user_id}/sales_projects/{person_id}"
        new_folder = f"foto/{user_id}/sales_projects/{backup_table_name}"
        if os.path.exists(old_folder):
            os.rename(old_folder, new_folder)

        # Update photo_path in backup table
        self.cursor.execute(f"UPDATE {backup_table_name} SET photo_path = REPLACE(photo_path, ?, ?)", (old_folder, new_folder))

        # Clear data for this person from the original table
        if table_name == 'sales_projects':
            self.cursor.execute(f"DELETE FROM {table_name} WHERE sales_id = ? AND user_id = ?", (person_id, user_id))
        elif table_name == 'worker_projects':
            self.cursor.execute(f"DELETE FROM {table_name} WHERE tukang_id = ? AND user_id = ?", (person_id, user_id))
    
        self.conn.commit()
        return backup_table_name


    def get_closed_books_for_person(self, table_name, person_id, user_id):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{table_name}_backup_{person_id}_{user_id}_%'")
        return [row[0] for row in self.cursor.fetchall()]

    def close_book(self, table_name, user_id):
        current_date = datetime.now()
        year, month, day = current_date.year, current_date.month, current_date.day
    
        # Dapatkan jumlah backup yang sudah ada untuk bulan ini
        self.cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name LIKE '{table_name}_backup_{user_id}_{year}_{month}%'")
        count = self.cursor.fetchone()[0] + 1
    
        # Buat nama tabel backup baru
        backup_table_name = f"{table_name}_backup_{user_id}_{year}_{month}_{day}_{count}"
    
        # Buat backup tabel
        self.cursor.execute(f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name} WHERE user_id = ?", (user_id,))
    
        # Clear original table
        self.cursor.execute(f"DELETE FROM {table_name} WHERE user_id = ?", (user_id,))
    
        self.conn.commit()
        return backup_table_name
    
    def get_closed_books(self, table_name, user_id):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{table_name}_backup_{user_id}_%'")
        return [row[0] for row in self.cursor.fetchall()]

    def load_closed_book(self, backup_table_name):
        self.cursor.execute(f"SELECT * FROM {backup_table_name}")
        return self.cursor.fetchall()
    
    def add_to_closed_book(self, backup_table_name, data, photo_path=None, user_id=None, person_id=None):
        table_name = backup_table_name.split('_backup_')[0]
        mapping = COLUMN_MAPPINGS.get(table_name, {})
        mapped_data = {mapping.get(k, k): v for k, v in data.items()}

        new_id = self.get_next_id(backup_table_name)
        mapped_data['id'] = new_id

        actual_columns = self.get_table_columns(backup_table_name)
        filtered_data = {k: v for k, v in mapped_data.items() if k in actual_columns}

        columns = ', '.join([f'"{key}"' for key in filtered_data.keys()])
        placeholders = ', '.join(['?' for _ in filtered_data])
        query = f'INSERT INTO "{backup_table_name}" ({columns}) VALUES ({placeholders})'

        self.cursor.execute(query, tuple(filtered_data.values()))

        if photo_path:
            new_photo_path = self.save_project_photo(user_id, person_id, mapped_data['customer_name'], photo_path, is_tukang='worker' in table_name, is_history=True, backup_table_name=backup_table_name)
            self.cursor.execute(f'UPDATE "{backup_table_name}" SET photo_path = ? WHERE id = ?', (new_photo_path, new_id))

        self.conn.commit()
        return new_id

    def get_next_id(self, table_name):
        self.cursor.execute(f"SELECT MAX(id) FROM {table_name}")
        max_id = self.cursor.fetchone()[0]
        return (max_id or 0) + 1

    def update_in_closed_book(self, backup_table_name, record_id, data, photo_path=None, user_id=None, person_id=None):
        table_name = backup_table_name.split('_backup_')[0]
        mapping = COLUMN_MAPPINGS.get(table_name, {})
        mapped_data = {mapping.get(k, k): v for k, v in data.items()}

        actual_columns = self.get_table_columns(backup_table_name)
        filtered_data = {k: v for k, v in mapped_data.items() if k in actual_columns and k != 'id'}

        set_clause = ', '.join([f'"{col}" = ?' for col in filtered_data.keys()])
        query = f'UPDATE "{backup_table_name}" SET {set_clause} WHERE id = ?'
        values = list(filtered_data.values()) + [record_id]

        self.cursor.execute(query, values)

        if photo_path:
            new_photo_path = self.save_project_photo(user_id, person_id, mapped_data['customer_name'], photo_path, is_tukang='worker' in table_name, is_history=True, backup_table_name=backup_table_name)
            self.cursor.execute(f'UPDATE "{backup_table_name}" SET photo_path = ? WHERE id = ?', (new_photo_path, record_id))

        self.conn.commit()

    def delete_from_closed_book(self, backup_table_name, record_id):
        query = f"DELETE FROM {backup_table_name} WHERE id = ?"
        self.cursor.execute(query, (record_id,))
        self.conn.commit()
    
    def update_consumer(self, consumer_id, data, user_id):
        self.cursor.execute('''
        UPDATE consumers
        SET date=?, name=?, address=?, sales=?, job=?, total_projects=?, worker=?, notes=?
        WHERE id=? AND user_id=?
        ''', (*data, consumer_id, user_id))
        self.conn.commit()


    def update_sales_project(self, project_id, data, user_id, photo_path=None):
        self.cursor.execute('''
        UPDATE sales_projects
        SET customer_name=?, address=?, job=?, total_project=?, commission=?, kb=?, notes=?
        WHERE id=? AND user_id=?
        ''', (*data, project_id, user_id))

        if photo_path:
            # Get the current photo path
            self.cursor.execute('SELECT photo_path FROM sales_projects WHERE id = ?', (project_id,))
            current_photo_path = self.cursor.fetchone()[0]

            # Delete the old photo if it exists
            if current_photo_path and os.path.exists(current_photo_path):
                os.remove(current_photo_path)

            # Save the new photo
            sales_project = self.cursor.execute('SELECT sales_id FROM sales_projects WHERE id = ?', (project_id,)).fetchone()
            if sales_project:
                sales_id = sales_project[0]
                new_photo_path = self.save_project_photo(user_id, sales_id, data[0], photo_path)
                self.cursor.execute('''
                UPDATE sales_projects SET photo_path = ? WHERE
                 id = ?
                ''', (new_photo_path, project_id))

        self.conn.commit()

    def update_worker_project(self, project_id, data, user_id, photo_path=None):
        self.cursor.execute('''
        UPDATE worker_projects SET customer_name=?, address=?, job=?, size=?, kb=?, notes=?
        WHERE id=? AND user_id=?
        ''', (*data, project_id, user_id))
        if photo_path:
            new_photo_path = self.save_project_photo(user_id, data[0], data[1], photo_path, is_tukang=True)
            self.cursor.execute('''
            UPDATE worker_projects SET photo_path = ? WHERE id = ?
            ''', (new_photo_path, project_id))
        self.conn.commit()

    def update_material_usage(self, material_id, data, user_id):
        self.cursor.execute('''
        UPDATE materials_usage
        SET date=?, item_name=?, quantity=?, unit_price=?, total=?, notes=?
        WHERE id=? AND user_id=?
        ''', (*data, material_id, user_id))
        self.conn.commit()
    
    def update_project(self, data, user_id):
        self.cursor.execute('''
        UPDATE projects
        SET name=?, sales_name=?, worker_name=?, start_date=?, end_date=?, total_project=?, dp=?
        WHERE id=? AND user_id=?
        ''', (*data, user_id))
        self.conn.commit()

    def delete_project(self, project_id, user_id):
        self.cursor.execute("DELETE FROM materials_usage WHERE project_id=? AND user_id=?", (project_id, user_id))
        self.cursor.execute("DELETE FROM projects WHERE id=? AND user_id=?", (project_id, user_id))
        self.conn.commit()

    def get_table_columns(self, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return [column[1] for column in self.cursor.fetchall()]

    def insert_tukang(self, name, user_id):
        self.cursor.execute('INSERT INTO tukang (name, user_id) VALUES (?, ?)', (name, user_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_tukang_list(self, user_id):
        self.cursor.execute('SELECT * FROM tukang WHERE user_id = ?', (user_id,))
        return self.cursor.fetchall()

    def get_tukang(self, tukang_id, user_id):
        self.cursor.execute('SELECT * FROM tukang WHERE id = ? AND user_id = ?', (tukang_id, user_id))
        return self.cursor.fetchone()

    def update_tukang(self, tukang_id, name, user_id):
        self.cursor.execute('UPDATE tukang SET name = ? WHERE id = ? AND user_id = ?', (name, tukang_id, user_id))
        self.conn.commit()

    def delete_tukang(self, tukang_id, user_id):
        self.cursor.execute('DELETE FROM worker_projects WHERE tukang_id = ? AND user_id = ?', (tukang_id, user_id))
        self.cursor.execute('DELETE FROM tukang WHERE id = ? AND user_id = ?', (tukang_id, user_id))
        self.conn.commit()
    
    def get_worker_project_photo(self, project_id, user_id):
        self.cursor.execute('''
        SELECT photo_path FROM worker_projects WHERE id = ? AND user_id = ?
        ''', (project_id, user_id))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def insert_worker_project(self, tukang_id, data, year, month, user_id, photo_path=None):
        self.cursor.execute('''
        INSERT INTO worker_projects (tukang_id, customer_name, address, job, size, kb, notes, year, month, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tukang_id, *data, year, month, user_id))
        new_id = self.cursor.lastrowid
        if photo_path:
            new_photo_path = self.save_project_photo(user_id, tukang_id, data[0], photo_path, is_tukang=True)
            self.cursor.execute('''
            UPDATE worker_projects SET photo_path = ? WHERE id = ?
            ''', (new_photo_path, new_id))
        self.conn.commit()
        return new_id

    def migrate_sales_table(self):
        # Check if the sales_id column exists in sales_projects
        self.cursor.execute("PRAGMA table_info(sales_projects)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        if 'sales_id' not in columns:
            # Add sales_id column to sales_projects
            self.cursor.execute("ALTER TABLE sales_projects ADD COLUMN sales_id INTEGER")
            
            # Create sales table if it doesn't exist
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                user_id INTEGER
            )
            ''')
            
            # Migrate existing data
            self.cursor.execute("SELECT DISTINCT sales, user_id FROM sales_projects")
            unique_sales = self.cursor.fetchall()
            
            for sale, user_id in unique_sales:
                self.cursor.execute("INSERT OR IGNORE INTO sales (name, user_id) VALUES (?, ?)", (sale, user_id))
                self.cursor.execute("UPDATE sales_projects SET sales_id = (SELECT id FROM sales WHERE name = ? AND user_id = ?) WHERE sales = ? AND user_id = ?", (sale, user_id, sale, user_id))
            
            # Remove the old sales column
            self.cursor.execute("CREATE TABLE sales_projects_new AS SELECT id, sales_id, customer_name, address, job, total_project, commission, kb, notes, year, month, user_id FROM sales_projects")
            self.cursor.execute("DROP TABLE sales_projects")
            self.cursor.execute("ALTER TABLE sales_projects_new RENAME TO sales_projects")
            
            self.conn.commit()

    def insert_sales(self, name, user_id):
        self.cursor.execute('INSERT INTO sales (name, user_id) VALUES (?, ?)', (name, user_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_sales_list(self, user_id):
        self.cursor.execute('SELECT * FROM sales WHERE user_id = ?', (user_id,))
        return self.cursor.fetchall()

    def get_sales(self, sales_id, user_id):
        self.cursor.execute('SELECT * FROM sales WHERE id = ? AND user_id = ?', (sales_id, user_id))
        return self.cursor.fetchone()

    def update_sales(self, sales_id, name, user_id):
        self.cursor.execute('UPDATE sales SET name = ? WHERE id = ? AND user_id = ?', (name, sales_id, user_id))
        self.conn.commit()

    def delete_sales(self, sales_id, user_id):
        self.cursor.execute('DELETE FROM sales_projects WHERE sales_id = ? AND user_id = ?', (sales_id, user_id))
        self.cursor.execute('DELETE FROM sales WHERE id = ? AND user_id = ?', (sales_id, user_id))
        self.conn.commit()

    def get_sales_projects(self, sales_id, user_id):
        self.cursor.execute('''
        SELECT id, customer_name, address, job, total_project, commission, kb, notes 
        FROM sales_projects 
        WHERE sales_id = ? AND user_id = ?
        ''', (sales_id, user_id))
        return self.cursor.fetchall()

    def insert_sales_project(self, sales_id, data, year, month, user_id, photo_path=None):
        self.cursor.execute('''
        INSERT INTO sales_projects (sales_id, customer_name, address, job, total_project, commission, kb, notes, year, month, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (sales_id, *data, year, month, user_id))
        new_id = self.cursor.lastrowid
    
        if photo_path:
            new_photo_path = self.save_project_photo(user_id, sales_id, data[0], photo_path)
            self.cursor.execute('''
            UPDATE sales_projects SET photo_path = ? WHERE id = ?
            ''', (new_photo_path, new_id))
    
        self.conn.commit()
        return new_id

    
    def save_project_photo(self, user_id, person_id, customer_name, photo_path, is_tukang=False, is_history=False, backup_table_name=None):
        if is_history:
            directory = f"foto/{user_id}/{backup_table_name}/{person_id}"
        else:
            directory = f"foto/{user_id}/{'worker_projects' if is_tukang else 'sales_projects'}/{person_id}"
        os.makedirs(directory, exist_ok=True)
        file_extension = os.path.splitext(photo_path)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        new_photo_path = os.path.join(directory, unique_filename)
        shutil.copy(photo_path, new_photo_path)
        return new_photo_path


    def get_sales_project_photo(self, project_id, user_id):
        self.cursor.execute('''
        SELECT photo_path FROM sales_projects WHERE id = ? AND user_id = ?
        ''', (project_id, user_id))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def __del__(self):
        self.conn.close()