import pyautogui as pg


pg.FAILSAFE = False

pg.PAUSE = 1.0


def get_screenshot(save: bool = False):
    """
    スクリーンショットを取得する
    """
    screenshot = pg.screenshot()

    if save:
        screenshot.save("pyautogui_screenshot.png")
    return screenshot


def get_cursor_position():
    """
    マウスカーソルの位置を取得する
    """
    position = pg.position()
    return position


def get_size():
    """
    画面のサイズを取得する
    """

    # マルチモニタを使っていても認識しないよう

    # プライマリモニタのみを認識する

    # Size(width=1920, height=1080)

    size = pg.size()

    return size


def move_cursor(loc: tuple[int, int]):
    """
    カーソルを移動する
    Args:
        loc: 移動する座標
    """
    pg.moveTo(loc)


def shortcut():
    pg.hotkey("ctrl", "A")


if __name__ == "__main__":
    # print(get_size())
    # print(get_cursor_position())
    # get_screenshot()()
    # move_cursor((100, 100))
    shortcut()
