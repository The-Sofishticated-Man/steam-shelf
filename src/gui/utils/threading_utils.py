import threading
import tkinter as tk
from typing import Callable, Any, Optional
from functools import wraps


class ThreadManager:
    """Manages background operations in GUI applications."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the thread manager.
        
        Args:
            root: The main tkinter window for scheduling UI updates
        """
        self.root = root
        self._active_threads = set()
    
    def run_in_background(self, 
                         operation: Callable,
                         on_success: Optional[Callable] = None,
                         on_error: Optional[Callable] = None,
                         on_progress: Optional[Callable] = None,
                         args: tuple = (),
                         kwargs: dict = None):
        """Run an operation in a background thread.
        
        Args:
            operation: Function to run in background
            on_success: Callback when operation succeeds (called with result)
            on_error: Callback when operation fails (called with exception)
            on_progress: Callback for progress updates (called with progress info)
            args: Arguments to pass to operation
            kwargs: Keyword arguments to pass to operation
        """
        if kwargs is None:
            kwargs = {}
            
        def thread_wrapper():
            try:
                # Call the operation
                result = operation(*args, **kwargs)
                
                # Schedule success callback on main thread
                if on_success:
                    self.root.after(0, lambda: on_success(result))
                    
            except Exception as e:
                # Schedule error callback on main thread
                if on_error:
                    self.root.after(0, lambda: on_error(e))
            finally:
                # Remove thread from active set
                thread = threading.current_thread()
                self._active_threads.discard(thread)
        
        # Create and start thread
        thread = threading.Thread(target=thread_wrapper, daemon=True)
        self._active_threads.add(thread)
        thread.start()
        
        return thread
    
    def is_operation_running(self) -> bool:
        """Check if any background operations are running."""
        # Clean up finished threads
        self._active_threads = {t for t in self._active_threads if t.is_alive()}
        return len(self._active_threads) > 0
    
    def wait_for_all(self, timeout: float = None):
        """Wait for all background operations to complete.
        
        Args:
            timeout: Maximum time to wait (None for indefinite)
        """
        for thread in list(self._active_threads):
            if thread.is_alive():
                thread.join(timeout)


def threaded_operation(thread_manager: ThreadManager):
    """Decorator to make a method run in background thread.
    
    Args:
        thread_manager: ThreadManager instance to use
        
    Usage:
        @threaded_operation(self.thread_manager)
        def my_long_operation(self, success_callback, error_callback):
            # Long running operation
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, success_callback=None, error_callback=None, *args, **kwargs):
            # Extract callbacks from kwargs if they're there
            success_cb = kwargs.pop('success_callback', success_callback)
            error_cb = kwargs.pop('error_callback', error_callback)
            
            # Define the actual operation (without callbacks)
            def operation():
                return func(self, *args, **kwargs)
            
            # Run in background
            return thread_manager.run_in_background(
                operation=operation,
                on_success=success_cb,
                on_error=error_cb
            )
        return wrapper
    return decorator


class ProgressCallback:
    """Helper class for progress reporting in threaded operations."""
    
    def __init__(self, root: tk.Tk, callback: Callable[[str, float], None]):
        """Initialize progress callback.
        
        Args:
            root: Main tkinter window
            callback: Function to call with (message, progress) where progress is 0.0-1.0
        """
        self.root = root
        self.callback = callback
    
    def update(self, message: str, progress: float = None):
        """Update progress.
        
        Args:
            message: Progress message
            progress: Progress value from 0.0 to 1.0 (None for indeterminate)
        """
        # Schedule callback on main thread
        self.root.after(0, lambda: self.callback(message, progress))


class CancellableOperation:
    """Wrapper for operations that can be cancelled."""
    
    def __init__(self):
        self._cancelled = threading.Event()
    
    def cancel(self):
        """Cancel the operation."""
        self._cancelled.set()
    
    def is_cancelled(self) -> bool:
        """Check if operation has been cancelled."""
        return self._cancelled.is_set()
    
    def check_cancelled(self):
        """Raise an exception if operation has been cancelled."""
        if self.is_cancelled():
            raise OperationCancelledException("Operation was cancelled")


class OperationCancelledException(Exception):
    """Exception raised when an operation is cancelled."""
    pass