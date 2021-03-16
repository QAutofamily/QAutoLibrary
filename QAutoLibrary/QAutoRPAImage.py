import tempfile
import cv2, win32gui, win32con, win32api, numpy as np
import time

from typing import Union, List
from pathlib import Path
from PIL import ImageGrab


class Point2D:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def to_tuple(self) -> tuple:
        return (self.x,self.y)


class Region:
    def __init__(self, x: int, y: int, x2: int, y2: int):
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2

    def to_tuple(self) -> tuple:
        return (self.x, self.y, self.x2, self.y2)


class RGB:
    def __init__(self, red: int, green: int, blue:int):
        self.r = red
        self.g = green
        self.b = blue

    def to_color_ref(self) -> int:
        return int('%02x%02x%02x' % (self.b,self.g,self.r), 16)


class QAutoRPAImage():

    def __init__(self):
        pass

    @classmethod
    def find_image(cls, path_to_image: Union[Path,str]) -> Union[Region, None]:
        """[summary]

        Args:
            path_to_image (Union[Path,str]): [description]

        Returns:
            Union[Region, None]: [description]
        """
        outline = None

        # Tempfile, koska en keksinyt miten tehdä muokkaukset binäärinä
        tmpfile = tempfile.NamedTemporaryFile(suffix='.png')
        tmpfile.close()

        # Screenshot. Tän voinee tehdä myös binäärinä ilman tallennusta...
        scrshot = ImageGrab.grab()
        tmp = cv2.cvtColor(np.array(scrshot), cv2.COLOR_RGB2BGR)
        cv2.imwrite(tmpfile.name, tmp)

        img_rgb = cv2.imread(tmpfile.name, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(path_to_image, cv2.IMREAD_GRAYSCALE)

        w, h = template.shape[::-1]

        result = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= 0.9)

        if len(list(zip(*loc))) <= 0:
            return None

        # Jos nyt koitetaan eka vaan yhdellä.
        for pt in zip(*loc[::-1]):
            outline = Region(pt[0], pt[1], pt[0] + w, pt[1] + h)
            break

        cls.draw_rectangle(outline)

        Path(tmpfile.name).unlink()
        return outline

    @classmethod
    def get_center_point(cls, outline: Region) -> Point2D:
        """[summary]

        Args:
            outline (Region): [description]

        Returns:
            Point2D: [description]
        """
        return Point2D(int((outline.x + outline.x2) / 2), int((outline.y + outline.y2) / 2))

    @classmethod
    def draw_line(cls, points: List[Point2D], color: RGB = None) -> None:
        """[summary]

        Args:
            points (List[Point2D]): [description]
            color (RGB, optional): [description]. Defaults to None.
        """
        if not color:
            color = RGB(0, 255, 0)

        # GetDC(hwnd), jos haluaa nimenomaan tietylle ikkunalle...
        dc = win32gui.GetDC(0)
        pen = win32gui.CreatePen(win32con.PS_SOLID, 2, color.to_color_ref())
        win32gui.SelectObject(dc, pen)

        lista = [p.to_tuple() for p in points]
        win32gui.Polyline(dc, lista)

        win32gui.DeleteObject(pen)
        win32gui.DeleteDC(dc)

    @classmethod
    def draw_rectangle(cls, region: Region, color: RGB = None) -> None:
        """Draws a colour bordered transparent rectangle around given region

        Args:
            region (Region): [description]
            color (RGB, optional): [description]. Defaults to None.
        """
        if not color:
            color = RGB(0, 255, 0)
        dc = win32gui.GetDC(0)

        pen = win32gui.CreatePen(win32con.PS_SOLID, 2, color.to_color_ref())
        brush = win32gui.CreateBrushIndirect({'Style': win32con.BS_NULL, 'Color': -1, 'Hatch': win32con.HS_DIAGCROSS})
        win32gui.SelectObject(dc, pen)
        win32gui.SelectObject(dc, brush)
        win32gui.Rectangle(dc, *region.to_tuple())

        win32gui.DeleteObject(pen)
        win32gui.DeleteObject(brush)
        win32gui.DeleteDC(dc)

    @classmethod
    def draw_focus_rectangle(cls, region: Region) -> None:
        """Draw a highlight region around given region

        Args:
            region (Region): [description]
        """
        dc = win32gui.GetDC(0)
        pen = win32gui.CreatePen(win32con.PS_SOLID, 2, 0)
        win32gui.DrawFocusRect(dc, region.to_tuple())
        win32gui.SelectObject(dc, pen)
        win32gui.DeleteDC(dc)

    @classmethod
    def draw_ellipse(cls, region: Region, color: RGB = None) -> None:
        """Draws a colored ellipse around given region

        Args:
            region (Region): [description]
            color (RGB, optional): [description]. Defaults to None.
        """
        if not color:
            color = RGB(0, 255, 0)
        dc = win32gui.GetDC(0)

        pen = win32gui.CreatePen(win32con.PS_SOLID, 2, color.to_color_ref())
        brush = win32gui.CreateBrushIndirect({'Style': win32con.BS_NULL, 'Color': -1, 'Hatch': win32con.HS_DIAGCROSS})
        win32gui.SelectObject(dc, pen)
        win32gui.SelectObject(dc, brush)
        win32gui.Ellipse(dc, *region.to_tuple())

        win32gui.DeleteObject(pen)
        win32gui.DeleteObject(brush)
        win32gui.DeleteDC(dc)

    @classmethod
    def wait_for_image(cls, image, timeout=30):
        """Waits for image and returns center point

        Args:
            image (path): [description] path to image file
            timeout (int, optional): [description]. default timeout 30
        """
        for x in range(timeout):
            time.sleep(1)
            found_image = cls.find_image(image)
            if found_image is not None:
                return cls.get_center_point(found_image)
        raise TimeoutError(f"Image: '{image}' was not found")

    @classmethod
    def click_image(cls, image, timeout=30):
        """Left clicks at center of image

        Args:
            image (path): [description] path to image file
            timeout (int, optional): [description]. default timeout 30
        """
        point = cls.wait_for_image(image, timeout)
        x, y = point.x, point.y
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    @classmethod
    def double_click_image(cls, image, timeout=30):
        """Double clicks at center of image

        Args:
            image (path): [description] path to image file
            timeout (int, optional): [description]. default timeout 30
        """
        point = cls.wait_for_image(image, timeout)
        x, y = point.x, point.y
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    @classmethod
    def right_click_image(cls, image, timeout=30):
        """Right clicks at center of image

        Args:
            image (path): [description] path to image file
            timeout (int, optional): [description]. default timeout 30
        """
        point = cls.wait_for_image(image, timeout)
        x, y = point.x, point.y
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)

