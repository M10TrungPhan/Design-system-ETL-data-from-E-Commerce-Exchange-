import os
import shutil


def get_number_image(dir):
    list_key = os.listdir(dir)
    total_image = 0
    for key in list_key:
        dir_key = dir + key +"\\"+ "image\\"
        number_image = 0
        for item in os.listdir(dir_key):
            dir_item = dir_key + item + "\\"
            number_image += len(os.listdir(dir_item))
        total_image += number_image
        print(f"{key}:{number_image}")
    print(f"TOTAL IMAGE: {total_image}")


def get_number_text(dir):
    list_key = os.listdir(dir)
    print(len(list_key))
    total_text = 0
    list_item = []
    for key in list_key:
        dir_key = dir + key +"\\"+ "text\\"
        number_text = len(os.listdir(dir_key))
        list_item += os.listdir(dir_key)
        total_text += number_text
        # for item in os.listdir(dir_key):
        #     dir_item = dir_key + item + "\\"
        #     number_text += len(os.listdir(dir_item))
        print(f"{key}:{number_text}")
    # print(total_text)
    print(f"TOTAL_TEXT {len(list_item)}")
    print(f"TOTAL_TEXT_UNIQUE {len(set(list_item))}")


def process_data(dir):
    list_key = os.listdir(dir)
    print(len(list_key))
    for key in list_key:
        print(key)
        dir_key_image = dir + key +"\\"+ "image\\"
        list_image = os.listdir(dir_key_image)
        dir_key_text = dir + key +"\\"+ "text\\"
        list_text = [item.replace(".json", "") for item in os.listdir(dir_key_text)]
        list_remove = list(set(list_image)^set(list_text))
        for item_remove in list_remove:
            if item_remove in list_image:
                shutil.rmtree(dir_key_image + item_remove)
                print(f"xxxx{item_remove}")
            if item_remove in list_text:
                os.remove(dir_key_text + item_remove +".json")
                print(f"yyy{item_remove}")

dir_1 = r"\\smb-ai.tmt.local\Public-AI\Public\Data\Clothing_shop\Ivymoda_shop\test_ivymoda\Mode_category\\"
dir_2 = r"\\172.29.13.24\tmtaishare\Data\Tiki\Ver_1\\"
dir_3 = "E:/test_coupletx/Mode_all_product/"
# get_number_image(dir_2)
# process_data(dir_2)

get_number_text(dir_1)
print("______________________________________________")
get_number_image(dir_1)

