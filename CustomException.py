# Custom exception class to detect which file and line number the exception was raised from, for better debugging and error handling in the Neo4j insertion operations.
import sys
import traceback

class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
    def __str__(self):
        _, _, tb = sys.exc_info()
        last_frame = traceback.extract_tb(tb)[-1]
        
        file_name = last_frame.filename
        line_no = last_frame.lineno
        
        return f"{self.message} (File: {file_name}, Line: {line_no})"