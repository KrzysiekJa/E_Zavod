import traceback
from PyQt6.QtCore import QObject

class DebugHelper:
    _instance = None
    
    def __init__(self):
        self.deleted_objects = set()
        self.access_log = []
        
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = DebugHelper()
        return cls._instance
    
    def log_deletion(self, obj, obj_name):
        """Log when an object is deleted"""
        msg = f"🔴 OBJECT DELETED: {obj_name} ({id(obj)})"
        print(msg)
        self.deleted_objects.add(id(obj))
        self.access_log.append(msg)
        traceback.print_stack(limit=5)
    
    def log_access(self, obj, obj_name, method):
        """Log when an object is accessed"""
        obj_id = id(obj)
        if obj_id in self.deleted_objects:
            msg = f"⚠️ ACCESS TO DELETED OBJECT: {obj_name} ({obj_id}) in {method}"
            print(msg)
            self.access_log.append(msg)
            traceback.print_stack(limit=10)
            return False
        return True
    
    def print_summary(self):
        """Print summary of all issues"""
        print("\n" + "="*50)
        print("DEBUG SUMMARY")
        print("="*50)
        for log in self.access_log:
            print(log)
        print("="*50)

debug = DebugHelper.instance()