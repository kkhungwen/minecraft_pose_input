from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtWidgets import QApplication, QMainWindow
from pynput.mouse import Controller
import sys
import time

# 滑鼠控制器
mouse = Controller()

class MouseThread(QThread):
    def __init__(self, speed=300):
        super().__init__()
        self.speed = speed
        self.direction = {'x': 0, 'y': 0}

    def run(self):
        last_time = time.time()  # 紀錄上次更新的時間
        while not self.isInterruptionRequested():  # QThread 中止請求檢查
            # 計算 deltaTime
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time

            # 按照設定的方向和 deltaTime 調整滑鼠移動距離
            move_x = self.direction['x'] * self.speed * delta_time
            move_y = self.direction['y'] * self.speed * delta_time

            #print(self.direction['x'],self.direction['y'],move_x,move_y)
            # 移動滑鼠
            mouse.move(int(move_x), int(move_y))
            time.sleep(0.01)  # 控制移動頻率

    @Slot(float, float)
    def set_direction(self, x, y):
        self.direction['x'] = x
        self.direction['y'] = y


