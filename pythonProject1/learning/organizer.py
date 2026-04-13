import os
import time
import shutil #专门处理文件复制、移动
from watchdog.observers import Observer #监视操作系统
from watchdog.events import FileSystemEventHandler



#定义要扫描的文件夹路径
TARGET_DIR = r'C:\Users\Lenovo\Desktop\my_downloads'

#创建字典定义映射规则
EXTENSION_MAP = {
    ".jpg": "Images",
    ".png": "Images",
    ".pdf": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".zip": "Archives",
    ".rar": "Archives"
}

def start_organizing():
    #确保该文件夹存在
    if not os.path.exists(TARGET_DIR):
        print(f"错误：找不到目录{TARGET_DIR}")
        return

    count = 0 #计数器：记录搬运多少文件

    #获取文件夹下所有内容
    #listdir返回一个列表
    items = os.listdir(TARGET_DIR)

    print(f"正在扫描：{TARGET_DIR}\n"+"-"*30)

    for item in items:
            #拼接完整路径，用于判断是文件还是文件夹
        full_path = os.path.join(TARGET_DIR, item)

        if os.path.isfile(full_path):
            #提取文件名和后缀
            #splitext会返回一个元组(Tuple): (文件名, 后缀)，即元组解包
            _, extension = os.path.splitext(item)
            #如果后缀为空，给它一个默认值
            #ext_display = extension if extension else "无后缀" #三元运算符，如果extension为真则赋值给ext_display
            extension = extension.lower() #转小写
            #print(f"文件：{item:20} | 后缀：{ext_display}") #{item:20}表示占20个字符宽度，右补空格

            #根据后缀决定去处，找不到就去Others
            folder_name = EXTENSION_MAP.get(extension, "Others")

            #构造目标文件夹的路径
            target_folder_path = os.path.join(TARGET_DIR, folder_name)

            #如果文件夹不存在，就创建它
            if not os.path.exists(target_folder_path):
                os.makedirs(target_folder_path)
                print(f"创建了新文件夹：{folder_name}")

            #构造目标文件的完整路径
            dest_path = os.path.join(target_folder_path, item)

            #跳过报错文件，防止崩溃退出
            try:
                shutil.move(full_path, dest_path)
                print(f"已移动 {item} -> {folder_name}")
                count += 1
            except Exception as e:
                print(f"移动 {item} 失败，原因：{e}")
    print(f"\n整理完成！共处理了{count}个文件。")

#事件处理器
class MyHandler(FileSystemEventHandler):
    #文件夹里有文件“创建”时，自动调用函数
    def on_created(self, event): #文件创建时触发；event记录变动信息
        #on_deleted：文件删除时触发    on_moved：文件移动或改名时触发
        if not event.is_directory: #判断是否为文件夹
            print(f"检测到新文件：{event.src_path}")
            start_organizing()


if __name__ == "__main__": #如果该文件可能被其他文件import，并且不希望下面的代码在导入时自动运行，就要加这一行
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, TARGET_DIR, recursive=False) #下达监视命令

    print(f"监控已启动，正在监听：{TARGET_DIR}")
    observer.start() #启动线程

    try:
        while True:
            time.sleep(1) #每秒轮询一次
    except KeyboardInterrupt:
        observer.stop() #按Ctrl+C停止
    observer.join() #主线程等待巡逻线程结束

