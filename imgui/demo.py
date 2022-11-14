import dearpygui.dearpygui as dpg
import time
dpg.create_context()
images = 20
num = 1
def loading_bar(num):
    while num != images:
        num += 1 
        print(num)
        time.sleep(1.5)
        dpg.configure_item("Image Slider", default_value =num)
        if num == images:
            dpg.configure_item("modal_id", show=False)
            break

with dpg.window(label="Delete Files", modal=True, show=False, tag="modal_id", 
no_title_bar=True,pos=(800/2 - 100, 600/2-100)):
    dpg.add_text("Images are loading...")
    dpg.add_separator()
    dpg.add_slider_int(label="Image", width=200, min_value=1,
     max_value=images, tag="Image Slider",enabled=False)




with dpg.window(label="Tutorial"):
    dpg.add_button(label="Open Dialog", callback=lambda: dpg.configure_item("modal_id", show=True))

dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()