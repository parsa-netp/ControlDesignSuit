import dearpygui.dearpygui as dpg

# Global node counter to ensure unique tags for nodes
node_counter = 0

def update_terminal_position(main_window, terminal_window, terminal_height):
    """Update the position of the terminal window to stay at the bottom of the main window."""
    if dpg.does_item_exist(main_window) and dpg.does_item_exist(terminal_window):
        # Get the size and position of the main window
        main_pos = dpg.get_item_pos(main_window)
        main_size = dpg.get_item_rect_size(main_window)

        # Calculate the new position for the terminal window
        terminal_pos = [main_pos[0], main_pos[1] + main_size[1] - terminal_height]

        # Update the terminal window's position
        dpg.set_item_pos(terminal_window, terminal_pos)

def print_main_window_size():
    if dpg.does_item_exist("Main"):
        width = dpg.get_viewport_client_height()
        height = dpg.get_viewport_client_height()
        print(f"Main Window - Width: {width}, Height: {height}")

def button_callback(sender, app_data, user_data):
    global node_counter
    node_editor_tag = user_data
    node_counter += 1

    width = dpg.get_item_width("Main") / 2
    height = dpg.get_item_height("Main") / 2

    with dpg.node(parent=node_editor_tag, label=f"Node {node_counter}", tag=f"node_{node_counter}", pos=[height, width]):
        with dpg.node_attribute(label=f"Input {node_counter}"):
            dpg.add_input_float(label=f"Input Float {node_counter}", width=150)
        with dpg.node_attribute(label=f"Output {node_counter}", attribute_type=dpg.mvNode_Attr_Output):
            dpg.add_input_float(label=f"Output Float {node_counter}", width=150)

def object_menu(node_editor_tag):
    with dpg.window(label="object menu", width=200, height=dpg.get_viewport_height(), no_move=True,
                    horizontal_scrollbar=True, no_close=True, no_collapse=True, tag="object_menu"):
        with dpg.child_window(label="Left Menu", width=200, height=dpg.get_viewport_height() - 50, border=True, tag="Left Menu"):
            dpg.add_text("Menu")
            dpg.add_separator()
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
    def link_callback(sender, app_data):
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)

    def delink_callback(sender, app_data):
        dpg.delete_item(app_data)

    with dpg.window(label="Node Editor", tag="Main", height=800, width=1080, no_move=True,
                    horizontal_scrollbar=True, no_close=True, no_collapse=True):
        with dpg.node_editor(callback=link_callback, delink_callback=delink_callback, tag="node_editor"):
            pass
    return "node_editor"

def setup_terminal():
    """Creates a terminal window at the bottom of the viewport."""
    with dpg.window(label="Terminal", tag="Terminal", width=1080, height=200, pos=[0, 600], no_close=True):
        terminal_log = dpg.add_text("Terminal Output:\n")
        dpg.add_separator()
        command_input = dpg.add_input_text(
            label="Command",
            hint="Enter Python command here",
            on_enter=True,
            callback=lambda sender, app_data: run_command(sender, app_data, terminal_log)
        )

def run_command(sender, app_data, terminal_log):
    """Executes a command and logs the output."""
    command = app_data
    try:
        result = eval(command)
        output = f"> {command}\n{result}\n"
    except Exception as e:
        output = f"> {command}\nError: {e}\n"

    current_text = dpg.get_item_label(terminal_log)
    dpg.configure_item(terminal_log, default_value=current_text + output)

class MainWindow:
    def __init__(self):
        self.context_name = "Main Window"
        self.node_editor_tag = None  # Tag of the node editor
        self.terminal_window_tag = None  # Tag of the terminal window

    def run(self):
        dpg.create_context()
        # Create the node editor and get its tag
        self.node_editor_tag = node_editor()
        # Add menu bar
        menu_bar()
        # Add terminal
        setup_terminal()
        # Store the terminal window tag
        self.terminal_window_tag = "Terminal"
        # Create viewport
        dpg.create_viewport(title='Control System Design', width=1080, height=800, vsync=True)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        # Set the primary window and create the object menu
        dpg.set_primary_window("Main", True)
        object_menu(self.node_editor_tag)

        while dpg.is_dearpygui_running():
            # Update the terminal window position
            update_terminal_position("Main", self.terminal_window_tag, 200)

            # Print the main window's size each frame
            print_main_window_size()
            # Render a frame
            dpg.render_dearpygui_frame()

        dpg.start_dearpygui()
        dpg.destroy_context()

# Create an instance of the MainWindow class and run the application
if __name__ == "__main__":
    app = MainWindow()
    app.run()
