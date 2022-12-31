import win32gui
import win32ui
import win32con

from PIL import Image


class Capturer:
    def __init__(self):
        self.screenshot = None

    def capture(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd == 0:
                return

            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            w = right - left
            h = bottom - top

            hwndDC = win32gui.GetDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

            saveDC.SelectObject(saveBitMap)

            saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
            saveBitMap.Paint(saveDC, (0, 0, 0, 0), (0, 0, 0, 0))

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            try:
                im = Image.frombuffer(
                    "RGB",
                    (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                    bmpstr,
                    "raw",
                    "BGRX",
                    0,
                    1,
                )
            except ValueError as e:
                print(e)
                return

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            self.screenshot = im
        except (win32ui.error, win32gui.error) as e:
            print(e)
