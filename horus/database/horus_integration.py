"""
Horus Database Integration
=========================

Setup and management of Horus data integration.
"""

from horus.utils.globals import horus_connector, search_dock, media_grid_dock


def setup_horus_integration():
    """Set up Horus data integration."""
    global horus_connector, search_dock, media_grid_dock

    try:
        # Import Horus data connector
        from media_browser.horus_data_connector import get_horus_connector
        
        # Initialize connector
        horus_connector = get_horus_connector()
        
        if horus_connector:
            print("✅ Horus data connector initialized")
            
            # Test connection
            try:
                projects = horus_connector.get_available_projects()
                print(f"✅ Found {len(projects)} available projects")
                
                # Update project dropdown if search panel exists
                search_widget = search_dock.widget() if search_dock else None
                if search_widget and hasattr(search_widget, 'project_combo'):
                    project_combo = search_widget.project_combo
                    
                    # Clear existing items except first
                    while project_combo.count() > 1:
                        project_combo.removeItem(1)
                    
                    # Add available projects
                    for project in projects:
                        project_combo.addItem(project)
                    
                    print(f"✅ Updated project dropdown with {len(projects)} projects")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not load projects: {e}")
                
        else:
            print("❌ Failed to initialize Horus data connector")
            
    except Exception as e:
        print(f"❌ Error setting up Horus integration: {e}")
        import traceback
        traceback.print_exc()


def refresh_horus_data():
    """Refresh Horus data."""
    try:
        global horus_connector
        
        if horus_connector:
            # Refresh connector data
            horus_connector.refresh()
            print("✅ Refreshed Horus data")
        else:
            print("⚠️  Horus connector not available")
            
    except Exception as e:
        print(f"❌ Error refreshing Horus data: {e}")


def load_media_in_rv(file_path):
    """Load media file in Open RV."""
    try:
        import rv.commands as rvc
        rvc.addSource(file_path)
        print(f"Loaded in RV: {file_path}")
    except Exception as e:
        print(f"Error loading in RV: {e}")
