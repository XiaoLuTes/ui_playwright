from pages.flutter_page import FlutterPage

def main():
    x, y = FlutterPage.get_current_mouse_position()
    print(x, y)
    abs_x = int(x / 2880 * 100)
    abs_y = int(y / 2880 * 100)
    print(abs_x, abs_y)


if __name__ == '__main__':
    main()
