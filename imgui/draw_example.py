import dearpygui.dearpygui as dpg

HEIGHT = 480
WIDTH = 640

prev_pos = None


def release_func(sender, app_data):
    global prev_pos
    prev_pos = None


def drag_func(sender, app_data):
    global prev_pos
    current_pos = dpg.get_drawing_mouse_pos()
    if not prev_pos:
        prev_pos = current_pos
        return

    if dpg.is_item_hovered("Canvas"):
        color = [255, 0, 0] if dpg.is_key_down(dpg.mvKey_Spacebar) else [255, 255, 255]
        canvas_pos = dpg.get_item_pos("Canvas")
        p2_pos = (prev_pos[0] - canvas_pos[0], prev_pos[1] - canvas_pos[1])
        p1_pos = (current_pos[0] - canvas_pos[0], current_pos[1] - canvas_pos[1])

        dpg.draw_line(p1_pos, p2_pos, color=color, parent="Canvas")

        prev_pos = current_pos


def main():
    dpg.create_context()

    with dpg.handler_registry():
        dpg.add_mouse_release_handler(callback=release_func)
        dpg.add_mouse_drag_handler(callback=drag_func)

    with dpg.window(label="Sample", tag="MainWindow"):
        dpg.add_drawlist(tag="Canvas", width=WIDTH, height=HEIGHT)

    dpg.create_viewport(title='Draw Test', width=WIDTH, height=HEIGHT)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("MainWindow", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


main()