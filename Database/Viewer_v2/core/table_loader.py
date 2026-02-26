"""
Table loading and data management.
Separates data loading from UI display.
"""

from config import MAX_TABLE_ROWS_PREVIEW


class TableLoader:
    """
    Loads and manages table data from database.
    Handles large tables with row limits for performance.
    """
    
    def __init__(self, database_connection):
        """
        Initialize table loader.
        
        Args:
            database_connection: DatabaseConnection object
        """
        self.db = database_connection
        
    def load_table_preview(self, table_name, max_rows=None):
        """
        Load table data with optional row limit for preview.
        
        Args:
            table_name: Name of table to load
            max_rows: Maximum number of rows to load (None for all)
            
        Returns:
            tuple: (column_names, data_rows, total_rows_in_db)
        """
        if max_rows is None:
            max_rows = MAX_TABLE_ROWS_PREVIEW
            
        try:
            # Get all column names first
            cursor = self.db.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            if not columns:
                return [], [], 0
                
            # Get total row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]
            
            # Load data with limit
            query = f"SELECT * FROM {table_name} LIMIT {max_rows}"
            cursor.execute(query)
            data = cursor.fetchall()
            
            return columns, data, total_rows
            
        except Exception as e:
            print(f"Error loading table {table_name}: {e}")
            return [], [], 0
            
    def search_in_table(self, table_name, search_value, max_results=100):
        """
        Search for value in specific table.
        
        Args:
            table_name: Table to search in
            search_value: Value to search for
            max_results: Maximum results to return
            
        Returns:
            list: List of (row_index, column_index) tuples where value was found
        """
        if not search_value:
            return []
            
        try:
            cursor = self.db.connection.cursor()
            
            # Get all column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Build search query for all columns
            search_results = []
            
            for col_idx, column in enumerate(columns):
                # Use LIKE for partial matching, case-insensitive
                query = f"""
                    SELECT rowid FROM {table_name} 
                    WHERE CAST({column} AS TEXT) LIKE ? 
                    LIMIT {max_results}
                """
                cursor.execute(query, (f"%{search_value}%",))
                
                for row in cursor.fetchall():
                    # We get rowid, need to map to table row index
                    # For simplicity, we'll store column index
                    # Row mapping will be done in UI
                    search_results.append((row[0], col_idx))
                    
            return search_results
            
        except Exception as e:
            print(f"Error searching in table {table_name}: {e}")
            return []