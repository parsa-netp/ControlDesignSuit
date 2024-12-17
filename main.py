import dearpygui.dearpygui as dpg

# Global node counter to ensure unique tags for nodes
node_counter = 0

def print_main_window_size():
    if dpg.does_item_exist("Main"):
        width = dpg.get_viewport_client_height()
        height = dpg.get_viewport_client_height()
        print(f"Main Window - Width: {width}, Height: {height}")


def update_menu_height():
    """Update the height and border of the object_menu dynamically."""
    viewport_height = dpg.get_viewport_height()
    viewport_width = dpg.get_viewport_width()

    # Update object_menu size and border
    if dpg.does_item_exist("object_menu"):
        dpg.configure_item("object_menu", height=viewport_height - 50, border=viewport_width > 500)
        dpg.configure_item("Left Menu", height=viewport_height - 70)  # Adjust Left Menu height

def button_callback(sender, app_data, user_data):
    """
    Callback for buttons. Adds a simple node to the node editor.
    user_data: Contains the node editor's tag.
    """
    global node_counter

    node_editor_tag = user_data  # Node editor tag passed as user data
    node_counter += 1  # Increment node counter to generate unique node tags

    width = dpg.get_item_width("Main") / 2
    height = dpg.get_item_height("Main") / 2

    with dpg.node(parent=node_editor_tag, label=f"Node {node_counter}", tag=f"node_{node_counter}",pos=[height,width]):
        with dpg.node_attribute(label=f"Input {node_counter}"):
            dpg.add_input_float(label=f"Input Float {node_counter}", width=150)
        with dpg.node_attribute(label=f"Output {node_counter}", attribute_type=dpg.mvNode_Attr_Output):
            dpg.add_input_float(label=f"Output Float {node_counter}", width=150)

def object_menu(node_editor_tag):
    """
    Creates the object menu with buttons.
    node_editor_tag: Tag of the node editor to add nodes to.
    """
    with dpg.window(label="object menu", width=200, height=dpg.get_viewport_height(), no_move=True,
                    horizontal_scrollbar=True, no_close=True, no_collapse=True, tag="object_menu"):
        with dpg.child_window(label="Left Menu", width=200, height=dpg.get_viewport_height() - 50, border=True, tag="Left Menu"):
            dpg.add_text("Menu")
            dpg.add_separator()
            # Pass node_editor_tag to the callback
            dpg.add_button(label="Add Node 1", callback=button_callback, user_data=node_editor_tag)
            dpg.add_button(label="Add Node 2", callback=button_callback, user_data=node_editor_tag)
            dpg.add_button(label="Add Node 3", callback=button_callback, user_data=node_editor_tag)
            dpg.add_button(label="Add Node 4", callback=button_callback, user_data=node_editor_tag)

def print_me():
    print("hello world")

def menu_bar():
    with dpg.viewport_menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Save", callback=print_me)
            dpg.add_menu_item(label="Save As", callback=print_me)

            with dpg.menu(label="Settings"):
                dpg.add_menu_item(label="Setting 1", callback=print_me, check=True)
                dpg.add_menu_item(label="Setting 2", callback=print_me)

        dpg.add_menu_item(label="Help", callback=print_me)

        with dpg.menu(label="Widget Items"):
            dpg.add_checkbox(label="Pick Me", callback=print_me)
            dpg.add_button(label="Press Me", callback=print_me)
            dpg.add_color_picker(label="Color Me", callback=print_me)

def node_editor():
    """
    Creates the node editor and returns its tag.
    """
    # callback runs when user attempts to connect attributes
    def link_callback(sender, app_data):
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)

    # callback runs when user attempts to disconnect attributes
    def delink_callback(sender, app_data):
        dpg.delete_item(app_data)

    with dpg.window(label="Node Editor", tag="Main",height=1080, width=1920, no_move=True,
                    horizontal_scrollbar=True, no_close=True, no_collapse=True):
        with dpg.node_editor(callback=link_callback, delink_callback=delink_callback, tag="node_editor"):
            pass  # Node editor starts empty
    return "node_editor"

class MainWindow:
    def __init__(self):
        self.context_name = "Main Window"
        self.node_editor_tag = None  # Tag of the node editor

    def run(self):
        dpg.create_context()
        # Create the node editor and get its tag
        self.node_editor_tag = node_editor()
        # Add menu bar
        menu_bar()
        # Create viewport
        dpg.create_viewport(title='Control System Design', width=1080, height=800,vsync=True)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        # Set the primary window and create the object menu
        dpg.set_primary_window("Main", True)
        object_menu(self.node_editor_tag)

        while dpg.is_dearpygui_running():
            # Print the main window's size each frame
            print_main_window_size()
            # Render a frame
            dpg.render_dearpygui_frame()

        # Start Dear PyGui
        dpg.start_dearpygui()
        dpg.destroy_context()

# Create an instance of the MainWindow class and run the application
if __name__ == "__main__":
    app = MainWindow()
    app.run()
