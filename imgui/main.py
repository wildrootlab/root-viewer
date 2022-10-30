from gc import callbacks
import dearpygui.dearpygui as dpg
import os
import numpy as np
from sympy import im
import config
import os
import regex as re
from PIL import Image
dpg.create_context()

def load_image(*args):
    global image, image_path
    num =  1
    images = os.listdir(tmp_img_path)
    image_path = os.path.join(tmp_img_path, images[num])

    width, height, channels, data = dpg.load_image(image_path)
    return width, height, channels, data

def add_image():
    width, height, channels, data = load_image()
    with dpg.texture_registry() as reg_id:
        texture_id = dpg.add_static_texture(width, height, data, parent=reg_id)
    return texture_id

def update_image(sender, app_data):
    num=int(app_data)
    images = os.listdir(tmp_img_path)
    images.sort(key=lambda f: int(re.sub('\D', '', f)))
    image_path = os.path.join(tmp_img_path, images[num-1])
    width, height, channels, data = dpg.load_image(image_path)
    with dpg.texture_registry() as reg_id:
        texture_id = dpg.add_static_texture(width, height, data, parent=reg_id)
    dpg.configure_item("Image", texture_tag=texture_id, tag="Image")

def resize_img():
    w_height, w_width = dpg.get_item_rect_size("Image Window")
    size = w_height
    dpg.set_item_height("drawlist", size)
    dpg.set_item_width("drawlist", size)
    dpg.configure_item("Image", pmin =(0, 0), pmax=(size, size), uv_min=(0, 0), uv_max=(1, 1), parent="drawlist")

def image_get_scroll(sender, app_data):
    if dpg.get_value("Drawing ROI"):
        vals = dpg.get_item_configuration("circle")
        radius = vals.get("radius")
        new_rad = radius + app_data
        dpg.configure_item("circle", radius=new_rad)
        circle_roi()

def enable_drawing():
    if dpg.get_value("Drawing ROI"):
        circle_roi()
    elif not dpg.get_value("Drawing ROI"):
        if dpg.does_item_exist("circle"):
            dpg.configure_item("circle", show=False)

def circle_roi():
    if not dpg.does_item_exist("circle"):
        dpg.draw_circle(center=(0,0), radius=5, thickness=3,
        color=(255, 0, 0, 255), parent="drawlist",tag="circle")
    if dpg.get_value("Drawing ROI") and dpg.is_item_hovered("Image Window"):
        dpg.configure_item("circle",center=dpg.get_drawing_mouse_pos(), thickness=1,
         color=(255, 0, 0, 255), parent="drawlist",tag="circle", show=True)

def create_roi():
    if dpg.get_value("Drawing ROI") and dpg.is_item_hovered("drawlist"):
        roi_tag = dpg.generate_uuid()
        with dpg.draw_node(parent="drawlist"):
            vals = dpg.get_item_configuration("circle")
            radius = vals.get("radius")
            dpg.draw_circle(center=dpg.get_drawing_mouse_pos(), radius=radius, thickness=1,
            color=(225, 0, 0, 225), fill=(235, 151, 151, 40), 
            parent="drawlist",tag=roi_tag)
            rois.append(roi_tag)

def create_vis():
    import matplotlib.pyplot as plt
    from skimage.draw import disk

    for roi in rois:
        vals = dpg.get_item_configuration(roi)
        x,y = vals.get("center")
        radius = vals.get("radius")
        arr = np.zeros((512,512))
        vals = dpg.get_item_configuration(rois[0])
        # for some reason x,y comes in reverse order
        rr, cc = disk([y,x], radius, shape=arr.shape)
        arr[rr, cc] = 1
        mask = arr.astype(int)
        mask = mask < 1

        change = []
        for file in os.listdir(tmp_img_path):
                image_path = os.path.join(tmp_img_path,file)
                image = plt.imread(image_path)
                arr=np.array(image)
                arr[mask] = 0
                change.append(np.sum(arr))
            
        # create plot
        y = list(change)
        x = np.linspace(1, len(y), len(y))
        dpg.add_line_series(x,y, label="Plot", parent="vis_y_axis")
    dpg.configure_item("vis", show=True)

def show_rois():
    for roi in rois:
        with dpg.table_row(parent="ROI Table"):
            with dpg.table_cell():
                dpg.add_button(label=f"ROI {roi}", callback=roi_stats, user_data=roi)
    dpg.configure_item("ROI Window", show=True)

def roi_stats(sender, app_data, user_data):
    dpg.get_item_configuration(user_data)
    dpg.configure_item(user_data, show=False)

with dpg.window(label="Plot", tag="vis",show=False):
    with dpg.plot(label="Line Series", height=400, width=800):
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="vis_y_axis")

with dpg.window(label="ROI's", tag="ROI Window", show=False):
        with dpg.table(header_row=False, tag="ROI Table"):
            dpg.add_table_column(label="ROI's", parent="ROI Table",tag="ROI Table Col")

# height + 40 to account for the window title bar
def image_window():
    i_width, i_height, channels, data = load_image()
    with dpg.window(label="Image Window",tag="Image Window",width=i_width,height=i_height+40,pos=(0,0),
        no_scrollbar=True,no_collapse=True,no_close=True,no_resize=True):
        with dpg.drawlist(width=i_width, height=i_height,tag="drawlist",parent="Image Window"):
            w_height, w_width = dpg.get_item_rect_size("Image Window")
            # create image
            dpg.draw_image(add_image(), (0, 0) , [i_width, i_height], tag="Image")
            # handle window resize
            with dpg.item_handler_registry(tag="window_handler"):
                dpg.add_item_hover_handler()
                dpg.add_item_resize_handler(callback=resize_img)
            # handle moue events
            with dpg.handler_registry():
                dpg.add_mouse_move_handler(callback=enable_drawing)
                dpg.add_mouse_wheel_handler(callback=image_get_scroll)
                dpg.add_mouse_click_handler(callback=create_roi)
    dpg.bind_item_handler_registry("Image Window", "window_handler")
# set up toolbar
def toolbar():
    with dpg.window(label="Tools", width=330, height=view_port_height, pos=(view_port_width-346,0)):
        dpg.add_slider_int(label="Image", width=200, min_value=1, max_value=1,
        default_value=1, callback=update_image,tag="Image Slider", show=False)
        dpg.add_checkbox(label="Enable Drawing", callback=circle_roi, tag="Drawing ROI",)
        dpg.add_button(label="Make Vis", callback=create_vis)
        with dpg.tree_node(label="ROI Tools", tag="ROI Tools"):
            with dpg.group(horizontal=True):
                dpg.add_button(label="ROI's", callback=show_rois)

def images_to_tmp(sender, app_data):
    """
    Copy desiered files with proper extension into tmp folder
    """
    if os.name == 'nt':
        __config_path_tmp = os.path.join(os.getenv('APPDATA'), '2P-Analyser', 'tmp')
        if not os.path.exists(__config_path_tmp):
            os.makedirs(__config_path_tmp)
    else:
        __config_path_tmp = os.path.join(os.path.expanduser('~'), '.2P-Analyser', 'tmp')
        if not os.path.exists(__config_path_tmp):
            os.makedirs(__config_path_tmp)
    
    __extensions = ("jpg", "jpeg", "png", "bmp", "psd", "gif","hdr","pic","ppm","pgm")
    # set path for tmp images folder
    __config_path_tmp_images = os.path.join(__config_path_tmp, 'images')
    if not os.path.exists(__config_path_tmp_images):
        os.makedirs(__config_path_tmp_images)
    # get list of files from file dialog
    directory = os.path.normpath(app_data.get("current_path"))
    num = 1
    # copy files with proper extension into tmp folder
    for file in os.listdir(directory):
        if file.endswith(tuple(__extensions)):
            os.system(f"copy {os.path.join(directory, file)} {os.path.join(__config_path_tmp_images,f'{num}.{os.path.splitext(file)[1]}')}")
            num += 1
        # if tif file check bit depth and convert to jpg
        elif file.endswith("tif"):
            im = np.array(Image.open(f"{os.path.join(directory, file)}"))
            if im.dtype == 'uint16':
                image = Image.fromarray(im / np.amax(im) * 255).convert('L')
                image.save(f"{os.path.join(__config_path_tmp_images, f'{num}.png')}")
            else:
                image = Image.fromarray(im).convert('L')
                image.save(f"{os.path.join(__config_path_tmp_images, f'{num}.png')}")
            num += 1
        else:
            pass
    dpg.configure_item("Image Slider", max_value=len(os.listdir(tmp_img_path)),show=True)
    image_window()

if __name__ == "__main__":
    _Temp = config.Temp()
    tmp_img_path = os.path.join(os.getenv('APPDATA'), '2P-Analyser', 'tmp', 'images')
    view_port_width = 1200
    view_port_height = 1000
    rois = []
    dpg.create_viewport(title="Hi", width=view_port_width, height=view_port_height)

    dpg.add_file_dialog(width=800, height=400,
        directory_selector=True, show=False, callback=images_to_tmp, tag="open_folder_file_dialog_id")
    dpg.add_file_dialog(width=800, height=400,
    directory_selector=True, show=False, callback=_Temp.convert_files, tag="convert_images_file_dialog_id")



    # Set up the menu bar
    with dpg.viewport_menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Open Files", callback=lambda: dpg.show_item("open_folder_file_dialog_id"))
            with dpg.menu(label="Settings"):
                dpg.add_menu_item(label="Convert Files", callback=lambda: dpg.show_item("convert_images_file_dialog_id"))
    
    toolbar()

view_port_width = 1200
view_port_height = 1000

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()