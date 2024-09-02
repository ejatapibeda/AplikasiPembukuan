import sqlite3
from datetime import datetime
from error_handling import setup_error_handling

COLUMN_MAPPINGS = {
    'consumers': {
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
        self.migrate_materials_usage_table()

    def create_tables(self):
        # Consumers table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS consumers (
            id INTEGER PRIMARY KEY,
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

        self.conn.commit()
    
    def migrate_materials_usage_table(self):
        # Check if unit_price column exists
        self.cursor.execute("PRAGMA table_info(materials_usage)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        if 'unit_price' not in columns:
            # Add unit_price column
            self.cursor.execute("ALTER TABLE materials_usage ADD COLUMN unit_price TEXT")
            
            # Update existing rows: set unit_price based on total and quantity
            self.cursor.execute("UPDATE materials_usage SET unit_price = CAST(total AS REAL) / CAST(quantity AS REAL) WHERE quantity != '0' AND quantity != ''")
            
            self.conn.commit()

    def insert_consumer(self, data, year, month, user_id):
        self.cursor.execute('''
        INSERT INTO consumers (name, address, sales, job, total_projects, worker, notes, year, month, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    
        # Inisialisasi counter
        counter = 1
    
        while True:
            # Buat nama tabel backup
            backup_table_name = f"{table_name}_backup_{person_id}_{user_id}_{year}_{month}_{day}_{counter}"
        
            # Cek apakah tabel dengan nama ini sudah ada
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (backup_table_name,))
            if not self.cursor.fetchone():
                # Jika tidak ada, gunakan nama ini
                break
        
            # Jika sudah ada, increment counter dan coba lagi
            counter += 1
    
        # Buat backup tabel
        if table_name == 'sales_projects':
            self.cursor.execute(f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name} WHERE sales_id = ? AND user_id = ?", (person_id, user_id))
        elif table_name == 'worker_projects':
            self.cursor.execute(f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name} WHERE tukang_id = ? AND user_id = ?", (person_id, user_id))
    
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
    
    def add_to_closed_book(self, backup_table_name, data):
        table_name = backup_table_name.split('_backup_')[0]
        mapping = COLUMN_MAPPINGS.get(table_name, {})
        mapped_data = {mapping.get(k, k): v for k, v in data.items()}

        # Generate a new ID
        new_id = self.get_next_id(backup_table_name)
        mapped_data['id'] = new_id

        actual_columns = self.get_table_columns(backup_table_name)
        filtered_data = {k: v for k, v in mapped_data.items() if k in actual_columns}

        columns = ', '.join([f'"{key}"' for key in filtered_data.keys()])
        placeholders = ', '.join(['?' for _ in filtered_data])
        query = f'INSERT INTO "{backup_table_name}" ({columns}) VALUES ({placeholders})'

        print(f"Query: {query}")
        print(f"Values: {tuple(filtered_data.values())}")

        self.cursor.execute(query, tuple(filtered_data.values()))
        self.conn.commit()
        return new_id

    def get_next_id(self, table_name):
        self.cursor.execute(f"SELECT MAX(id) FROM {table_name}")
        max_id = self.cursor.fetchone()[0]
        return (max_id or 0) + 1

    def update_in_closed_book(self, backup_table_name, record_id, data):
        table_name = backup_table_name.split('_backup_')[0]
        mapping = COLUMN_MAPPINGS.get(table_name, {})
        mapped_data = {mapping.get(k, k): v for k, v in data.items()}
    
        actual_columns = self.get_table_columns(backup_table_name)
    
        set_clause = ', '.join([f'"{col}" = ?' for col in actual_columns if col in mapped_data and col != 'id'])
        if not set_clause:
            print("No valid columns to update")
            return
    
        query = f'UPDATE "{backup_table_name}" SET {set_clause} WHERE id = ?'
        values = [mapped_data[col] for col in actual_columns if col in mapped_data and col != 'id'] + [record_id]
    
        print(f"Query: {query}")
        print(f"Values: {values}")
    
        self.cursor.execute(query, values)
        self.conn.commit()

    def delete_from_closed_book(self, backup_table_name, record_id):
        query = f"DELETE FROM {backup_table_name} WHERE id = ?"
        self.cursor.execute(query, (record_id,))
        self.conn.commit()
    
    def update_consumer(self, consumer_id, data, user_id):
        self.cursor.execute('''
        UPDATE consumers
        SET name=?, address=?, sales=?, job=?, total_projects=?, worker=?, notes=?
        WHERE id=? AND user_id=?
        ''', (*data, consumer_id, user_id))
        self.conn.commit()

    def update_sales_project(self, project_id, data, user_id):
        self.cursor.execute('''
        UPDATE sales_projects
        SET customer_name=?, address=?, job=?, total_project=?, commission=?, kb=?, notes=?
        WHERE id=? AND user_id=?
        ''', (*data, project_id, user_id))
        self.conn.commit()

    def update_worker_project(self, project_id, data, user_id):
        self.cursor.execute('''
        UPDATE worker_projects SET customer_name=?, address=?, job=?, size=?, kb=?, notes=?
        WHERE id=? AND user_id=?
        ''', (*data, project_id, user_id))
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

    def insert_worker_project(self, tukang_id, data, year, month, user_id):
        self.cursor.execute('''
        INSERT INTO worker_projects (tukang_id, customer_name, address, job, size, kb, notes, year, month, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tukang_id, *data, year, month, user_id))
        self.conn.commit()
        return self.cursor.lastrowid

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

    def insert_sales_project(self, sales_id, data, year, month, user_id):
        self.cursor.execute('''
        INSERT INTO sales_projects (sales_id, customer_name, address, job, total_project, commission, kb, notes, year, month, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (sales_id, *data, year, month, user_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def __del__(self):
        self.conn.close()