from windows_mcp.tree.config import (
    INTERACTIVE_CONTROL_TYPE_NAMES,
    DOCUMENT_CONTROL_TYPE_NAMES,
    INFORMATIVE_CONTROL_TYPE_NAMES,
    DEFAULT_ACTIONS,
    THREAD_MAX_RETRIES,
)
from uiautomation import (
    Control,
    ImageControl,
    ScrollPattern,
    WindowControl,
    Rect,
    GetRootControl,
    PatternId,
)
from windows_mcp.tree.views import (
    TreeElementNode,
    ScrollElementNode,
    Center,
    BoundingBox,
    TreeState,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from windows_mcp.tree.utils import random_point_within_bounding_box
from PIL import Image, ImageFont, ImageDraw
from windows_mcp.desktop.views import App
from typing import TYPE_CHECKING
from time import sleep
import logging
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

if TYPE_CHECKING:
    from windows_mcp.desktop.service import Desktop


class Tree:
    def __init__(self, desktop: "Desktop"):
        self.desktop = desktop
        screen_size = self.desktop.get_screen_size()
        self.dom_bounding_box: BoundingBox = None
        self.screen_box = BoundingBox(
            top=0,
            left=0,
            bottom=screen_size.height,
            right=screen_size.width,
            width=screen_size.width,
            height=screen_size.height,
        )

    def get_state(self, active_app: App, other_apps: list[App]) -> TreeState:
        root = GetRootControl()
        other_apps_handle = set(map(lambda other_app: other_app.handle, other_apps))
        apps = list(
            filter(
                lambda app: app.NativeWindowHandle not in other_apps_handle,
                root.GetChildren(),
            )
        )
        if active_app:
            apps = list(filter(lambda app: app.ClassName != "Progman", apps))
        interactive_nodes, scrollable_nodes = self.get_appwise_nodes(apps=apps)
        return TreeState(
            interactive_nodes=interactive_nodes, scrollable_nodes=scrollable_nodes
        )

    def get_appwise_nodes(
        self, apps: list[Control]
    ) -> tuple[list[TreeElementNode], list[ScrollElementNode]]:
        interactive_nodes, scrollable_nodes = [], []
        with ThreadPoolExecutor() as executor:
            retry_counts = {app: 0 for app in apps}
            future_to_app = {
                executor.submit(
                    self.get_nodes, app, self.desktop.is_app_browser(app)
                ): app
                for app in apps
            }
            while future_to_app:  # keep running until no pending futures
                for future in as_completed(list(future_to_app)):
                    app = future_to_app.pop(future)  # remove completed future
                    try:
                        result = future.result()
                        if result:
                            element_nodes, scroll_nodes = result
                            interactive_nodes.extend(element_nodes)
                            scrollable_nodes.extend(scroll_nodes)
                    except Exception as e:
                        retry_counts[app] += 1
                        logger.debug(
                            f"Error in processing node {app.Name}, retry attempt {retry_counts[app]}\nError: {e}"
                        )
                        if retry_counts[app] < THREAD_MAX_RETRIES:
                            new_future = executor.submit(
                                self.get_nodes, app, self.desktop.is_app_browser(app)
                            )
                            future_to_app[new_future] = app
                        else:
                            logger.error(
                                f"Task failed completely for {app.Name} after {THREAD_MAX_RETRIES} retries"
                            )
        return interactive_nodes, scrollable_nodes

    def iou_bounding_box(
        self,
        window_box: Rect,
        element_box: Rect,
    ) -> BoundingBox:
        # Step 1: Intersection of element and window (existing logic)
        intersection_left = max(window_box.left, element_box.left)
        intersection_top = max(window_box.top, element_box.top)
        intersection_right = min(window_box.right, element_box.right)
        intersection_bottom = min(window_box.bottom, element_box.bottom)

        # Step 2: Clamp to screen boundaries (new addition)
        intersection_left = max(self.screen_box.left, intersection_left)
        intersection_top = max(self.screen_box.top, intersection_top)
        intersection_right = min(self.screen_box.right, intersection_right)
        intersection_bottom = min(self.screen_box.bottom, intersection_bottom)

        # Step 3: Validate intersection
        if (
            intersection_right > intersection_left
            and intersection_bottom > intersection_top
        ):
            bounding_box = BoundingBox(
                left=intersection_left,
                top=intersection_top,
                right=intersection_right,
                bottom=intersection_bottom,
                width=intersection_right - intersection_left,
                height=intersection_bottom - intersection_top,
            )
        else:
            # No valid visible intersection (either outside window or screen)
            bounding_box = BoundingBox(
                left=0, top=0, right=0, bottom=0, width=0, height=0
            )
        return bounding_box

    def get_nodes(
        self, node: Control, is_browser: bool = False
    ) -> tuple[list[TreeElementNode], list[ScrollElementNode]]:
        """
        指定されたアプリケーションウィンドウ（node）内のUI要素ツリーを走査し、
        操作可能な要素（interactive_nodes）とスクロール可能な要素（scrollable_nodes）を抽出します。
        
        Args:
            node: 対象のアプリケーションのルートコントロール (UIAutomationのControl)
            is_browser: 対象がブラウザかどうか (ブラウザの場合はDOMツリーとして特別な処理が必要なため)
        """
        window_bounding_box = node.BoundingRectangle

        # --- 内部ヘルパー関数: 各種判定ロジック ---

        def is_element_visible(node: Control, threshold: int = 0):
            """
            要素が視覚的に認識可能か判定します。
            
            判定基準:
            1. BoundingRectangle（境界矩形）が空でないこと
            2. 面積が閾値(threshold)より大きいこと
            3. "IsOffscreen" プロパティが False（画面内にある）であること
               ただし、"EditControl"（入力欄）の場合は、システム上でオフスクリーン扱いでも
               操作対象とみなす場合があるため例外としてTrue扱いにしています。
            4. コントロール要素であること
            """
            is_control = node.IsControlElement
            box = node.BoundingRectangle
            if box.isempty():
                return False
            width = box.width()
            height = box.height()
            area = width * height
            # node.IsOffscreen が False ならば画面内。
            # EditControlは例外的に許可
            is_offscreen = (not node.IsOffscreen) or node.ControlTypeName in [
                "EditControl"
            ]
            return area > threshold and is_offscreen and is_control

        def is_element_enabled(node: Control):
            """要素が有効（IsEnabled）か判定します。無効なボタンなどを除外するために使用します。"""
            try:
                return node.IsEnabled
            except Exception:
                return False

        def is_default_action(node: Control):
            """
            要素がデフォルトのアクション（操作）を持っているか判定します。
            例: 'invoke'（押下）、'expand'（展開）など。
            これにより、単なるテキスト表示ではなく、何かアクションを起こせる要素かを見分けます。
            """
            legacy_pattern = node.GetLegacyIAccessiblePattern()
            default_action = legacy_pattern.DefaultAction.title()
            if default_action in DEFAULT_ACTIONS:
                return True
            return False

        def is_element_image(node: Control):
            """
            画像要素かどうかを判定します。
            単なる装飾的な画像（graphic）や、フォーカスできない画像は操作対象から除外するために使われます。
            """
            if isinstance(node, ImageControl):
                if (
                    node.LocalizedControlType == "graphic"
                    or not node.IsKeyboardFocusable
                ):
                    return True
            return False

        def is_element_text(node: Control):
            """
            テキスト情報を持つ要素かどうかを判定します。
            INFORMATIVE_CONTROL_TYPE_NAMES に含まれる要素（TextControlなど）で、
            可視・有効・画像でないものを対象とします。
            """
            try:
                if node.ControlTypeName in INFORMATIVE_CONTROL_TYPE_NAMES:
                    if (
                        is_element_visible(node)
                        and is_element_enabled(node)
                        and not is_element_image(node)
                    ):
                        return True
            except Exception:
                return False
            return False

        def is_window_modal(node: WindowControl):
            """ウィンドウがモーダル（親ウィンドウをブロックするタイプ）かどうかを判定します。"""
            try:
                window_pattern = node.GetWindowPattern()
                return window_pattern.IsModal
            except Exception:
                return False

        def is_keyboard_focusable(node: Control):
            """
            キーボードフォーカスを受け取れるか判定します。
            特定のコントロールタイプ（入力欄、ボタン、チェックボックスなど）は
            無条件でフォーカス可能とみなすホワイトリスト処理が含まれています。
            それ以外は IsKeyboardFocusable プロパティを確認します。
            """
            try:
                if node.ControlTypeName in set(
                    [
                        "EditControl",
                        "ButtonControl",
                        "CheckBoxControl",
                        "RadioButtonControl",
                        "TabItemControl",
                    ]
                ):
                    return True
                return node.IsKeyboardFocusable
            except Exception:
                return False

        def element_has_child_element(
            node: Control, control_type: str, child_control_type: str
        ):
            """
            指定されたコントロールタイプの子要素を持っているか確認します。
            DOM構造の補正（dom_correction）で使用されます。
            """
            if node.LocalizedControlType == control_type:
                first_child = node.GetFirstChildControl()
                if first_child is None:
                    return False
                return first_child.LocalizedControlType == child_control_type

        def group_has_no_name(node: Control):
            """名前（ラベル）のないグループコントロールか判定します。"""
            try:
                if node.ControlTypeName == "GroupControl":
                    if not node.Name.strip():
                        return True
                return False
            except Exception:
                return False

        def is_element_scrollable(node: Control):
            """
            要素がスクロール可能か判定します。
            1. リストやドキュメントなどの特定のコンテナタイプでない、あるいはオフスクリーンの場合は除外
            2. ScrollPattern を取得し、VerticallyScrollable（垂直スクロール可能）かチェック
            """
            try:
                if (
                    node.ControlTypeName
                    in INTERACTIVE_CONTROL_TYPE_NAMES | INFORMATIVE_CONTROL_TYPE_NAMES
                ) or node.IsOffscreen:
                    return False
                scroll_pattern: ScrollPattern = node.GetPattern(PatternId.ScrollPattern)
                if scroll_pattern is None:
                    return False
                return scroll_pattern.VerticallyScrollable
            except Exception:
                return False

        def is_element_interactive(node: Control):
            """
            要素が対話可能（クリックや入力が可能）な「インタラクティブ要素」かどうかを判定します。
            アプリの種類（ブラウザか否か）やコントロールタイプによって判定ロジックが分岐します。
            """
            try:
                # ブラウザ内のデータ項目やリスト項目で、キーボードフォーカスできないものは除外
                if (
                    is_browser
                    and node.ControlTypeName
                    in set(["DataItemControl", "ListItemControl"])
                    and not is_keyboard_focusable(node)
                ):
                    return False
                # ブラウザ以外で、画像のコントロールだがキーボードフォーカス可能な場合は対象とする
                elif (
                    not is_browser
                    and node.ControlTypeName == "ImageControl"
                    and is_keyboard_focusable(node)
                ):
                    return True
                # 一般的なインタラクティブ要素またはドキュメント要素の場合
                elif (
                    node.ControlTypeName
                    in INTERACTIVE_CONTROL_TYPE_NAMES | DOCUMENT_CONTROL_TYPE_NAMES
                ):
                    return (
                        is_element_visible(node)
                        and is_element_enabled(node)
                        and (not is_element_image(node) or is_keyboard_focusable(node))
                    )
                # グループコントロールの場合
                elif node.ControlTypeName == "GroupControl":
                    if is_browser:
                        return (
                            is_element_visible(node)
                            and is_element_enabled(node)
                            and (is_default_action(node) or is_keyboard_focusable(node))
                        )
                    # ブラウザ以外のGroupControlの処理はコメントアウトされています
                    # else:
                    #     return is_element_visible and is_element_enabled(node) and is_default_action(node)
            except Exception:
                return False
            return False

        def dom_correction(node: Control):
            """
            ブラウザのDOM構造特有の冗長性や入れ子構造を補正するための関数です。
            例えば、「リスト項目」の中に「リンク」がある場合など、重複して検出するのを防ぐために
            親要素を削除し、より適切な子要素を採用するなどの調整を行います。
            """
            # "list item"の中に"link"がある、あるいは"item"の中に"link"がある場合
            if element_has_child_element(
                node, "list item", "link"
            ) or element_has_child_element(node, "item", "link"):
                dom_interactive_nodes.pop()  # 直前に追加された親ノード（重複あるいは不要）を削除
                return None
            
            # グループコントロールの場合の処理
            elif node.ControlTypeName == "GroupControl":
                dom_interactive_nodes.pop() # 親グループを削除
                if is_keyboard_focusable(node):
                    child = node
                    try:
                        # 適切なテキストを持つ子要素を探す探索ロジック
                        while child.GetFirstChildControl() is not None:
                            if child.ControlTypeName in INTERACTIVE_CONTROL_TYPE_NAMES:
                                return None
                            child = child.GetFirstChildControl()
                    except Exception:
                        return None
                    if child.ControlTypeName != "TextControl":
                        return None
                    
                    # 適切な子要素が見つかった場合、その情報でノードを再作成して追加
                    legacy_pattern = node.GetLegacyIAccessiblePattern()
                    value = legacy_pattern.Value
                    element_bounding_box = node.BoundingRectangle
                    bounding_box = self.iou_bounding_box(
                        self.dom_bounding_box, element_bounding_box
                    )
                    center = bounding_box.get_center()
                    is_focused = node.HasKeyboardFocus
                    dom_interactive_nodes.append(
                        TreeElementNode(
                            **{
                                "name": child.Name.strip(),
                                "control_type": node.LocalizedControlType,
                                "value": value,
                                "shortcut": node.AcceleratorKey,
                                "bounding_box": bounding_box,
                                "xpath": "",
                                "center": center,
                                "app_name": app_name,
                                "is_focused": is_focused,
                            }
                        )
                    )
            # "link"の中に"heading"がある場合の処理
            elif element_has_child_element(node, "link", "heading"):
                dom_interactive_nodes.pop()
                node = node.GetFirstChildControl()
                control_type = "link"
                legacy_pattern = node.GetLegacyIAccessiblePattern()
                value = legacy_pattern.Value
                element_bounding_box = node.BoundingRectangle
                bounding_box = self.iou_bounding_box(
                    self.dom_bounding_box, element_bounding_box
                )
                center = bounding_box.get_center()
                is_focused = node.HasKeyboardFocus
                dom_interactive_nodes.append(
                    TreeElementNode(
                        **{
                            "name": node.Name.strip(),
                            "control_type": control_type,
                            "value": node.Name.strip(),
                            "shortcut": node.AcceleratorKey,
                            "bounding_box": bounding_box,
                            "xpath": "",
                            "center": center,
                            "app_name": app_name,
                            "is_focused": is_focused,
                        }
                    )
                )

        # --- ツリー走査のメインロジック ---

        def tree_traversal(
            node: Control, is_dom: bool = False, is_dialog: bool = False
        ):
            """
            再帰的にUIツリーを探索します。
            
            Args:
                node: 現在探索中のコントロール
                is_dom: 現在ブラウザのHTMLコンテンツ（DOM）内部にいるかどうか
                is_dialog: ダイアログの中にいるかどうか
            """
            # インタラクティブでない不要なノードをスキップするチェック
            if (
                node.IsOffscreen
                and (
                    node.ControlTypeName
                    not in set(["GroupControl", "EditControl", "TitleBarControl"])
                )
                and node.ClassName
                not in set(["Popup", "Windows.UI.Core.CoreComponentInputSource"])
            ):
                return None

            # スクロール可能な要素であればリストに追加
            if is_element_scrollable(node):
                scroll_pattern: ScrollPattern = node.GetPattern(PatternId.ScrollPattern)
                box = node.BoundingRectangle
                # 要素内のランダムな点を取得（操作点として使用）
                x, y = random_point_within_bounding_box(node=node, scale_factor=0.8)
                center = Center(x=x, y=y)
                scrollable_nodes.append(
                    ScrollElementNode(
                        **{
                            "name": node.Name.strip()
                            or node.AutomationId
                            or node.LocalizedControlType.capitalize()
                            or "''",
                            "app_name": app_name,
                            "control_type": node.LocalizedControlType.title(),
                            "bounding_box": BoundingBox(
                                **{
                                    "left": box.left,
                                    "top": box.top,
                                    "right": box.right,
                                    "bottom": box.bottom,
                                    "width": box.width(),
                                    "height": box.height(),
                                }
                            ),
                            "center": center,
                            "xpath": "",
                            "horizontal_scrollable": scroll_pattern.HorizontallyScrollable,
                            "horizontal_scroll_percent": scroll_pattern.HorizontalScrollPercent
                            if scroll_pattern.HorizontallyScrollable
                            else 0,
                            "vertical_scrollable": scroll_pattern.VerticallyScrollable,
                            "vertical_scroll_percent": scroll_pattern.VerticalScrollPercent
                            if scroll_pattern.VerticallyScrollable
                            else 0,
                            "is_focused": node.HasKeyboardFocus,
                        }
                    )
                )

            # インタラクティブな要素であればリストに追加
            if is_element_interactive(node):
                legacy_pattern = node.GetLegacyIAccessiblePattern()
                value = (
                    legacy_pattern.Value.strip()
                    if legacy_pattern.Value is not None
                    else ""
                )
                is_focused = node.HasKeyboardFocus
                name = node.Name.strip()
                element_bounding_box = node.BoundingRectangle
                
                # ブラウザDOM内の要素の場合
                if is_browser and is_dom:
                    bounding_box = self.iou_bounding_box(
                        self.dom_bounding_box, element_bounding_box
                    )
                    center = bounding_box.get_center()
                    tree_node = TreeElementNode(
                        **{
                            "name": name,
                            "control_type": node.LocalizedControlType.title(),
                            "value": value,
                            "shortcut": node.AcceleratorKey,
                            "bounding_box": bounding_box,
                            "center": center,
                            "xpath": "",
                            "app_name": app_name,
                            "is_focused": is_focused,
                        }
                    )
                    dom_interactive_nodes.append(tree_node)
                    # DOM構造の補正を実行
                    dom_correction(node=node)
                else:
                    # 通常のアプリ要素の場合
                    bounding_box = self.iou_bounding_box(
                        window_bounding_box, element_bounding_box
                    )
                    center = bounding_box.get_center()
                    tree_node = TreeElementNode(
                        **{
                            "name": name,
                            "control_type": node.LocalizedControlType.title(),
                            "value": value,
                            "shortcut": node.AcceleratorKey,
                            "bounding_box": bounding_box,
                            "center": center,
                            "xpath": "",
                            "app_name": app_name,
                            "is_focused": is_focused,
                        }
                    )
                    interactive_nodes.append(tree_node)
            # テキスト要素の場合の処理（コメントアウト中）
            # elif is_element_text(node):
            #     informative_nodes.append(TextElementNode(
            #         name=node.Name.strip() or "''",
            #         app_name=app_name
            #     ))

            children = node.GetChildren()

            # 子要素を再帰的に走査
            # DOM内では左から右（通常の順序）、通常のアプリでは右から左（逆順）で探索
            # 理由: UIの重ね合わせ順序やタブオーダーに関連している可能性があります
            for child in children if is_dom else children[::-1]:
                
                # ブラウザのレンダリング領域（Chrome_RenderWidgetHostHWND）に入った場合
                if is_browser and child.ClassName == "Chrome_RenderWidgetHostHWND":
                    bounding_box = child.BoundingRectangle
                    self.dom_bounding_box = BoundingBox(
                        left=bounding_box.left,
                        top=bounding_box.top,
                        right=bounding_box.right,
                        bottom=bounding_box.bottom,
                        width=bounding_box.width(),
                        height=bounding_box.height(),
                    )
                    # DOMサブツリーの走査を開始（is_dom=True）
                    tree_traversal(child, is_dom=True, is_dialog=is_dialog)
                
                # ダイアログウィンドウが見つかった場合
                elif isinstance(child, WindowControl):
                    if not child.IsOffscreen:
                        if is_dom:
                            bounding_box = child.BoundingRectangle
                            # ダイアログが画面の大半を覆っている場合、背後のDOM要素は無効とする
                            if bounding_box.width() > 0.8 * self.dom_bounding_box.width:
                                dom_interactive_nodes.clear()
                        else:
                            # モーダルダイアログの場合、背後のアプリ要素は無効とする
                            if is_window_modal(child):
                                interactive_nodes.clear()
                    # ダイアログサブツリーの走査を開始（is_dialog=True）
                    tree_traversal(child, is_dom=is_dom, is_dialog=True)
                else:
                    # 通常の子要素
                    tree_traversal(child, is_dom=is_dom, is_dialog=is_dialog)

        # --- 初期化と実行 ---
        interactive_nodes, dom_interactive_nodes, scrollable_nodes = [], [], []
        app_name = node.Name.strip()
        
        # 特定のクラス名に対してアプリ名を読みやすく変更
        match node.ClassName:
            case "Progman":
                app_name = "Desktop"
            case "Shell_TrayWnd" | "Shell_SecondaryTrayWnd":
                app_name = "Taskbar"
            case "Microsoft.UI.Content.PopupWindowSiteBridge":
                app_name = "Context Menu"
            case _:
                pass
        
        # 走査開始
        tree_traversal(node, is_dom=False, is_dialog=False)

        logger.debug(f"Interactive nodes:{len(interactive_nodes)}")
        logger.debug(f"DOM interactive nodes:{len(dom_interactive_nodes)}")
        logger.debug(f"Scrollable nodes:{len(scrollable_nodes)}")

        # 通常のインタラクティブノードとDOMインタラクティブノードを結合
        interactive_nodes.extend(dom_interactive_nodes)
        return (interactive_nodes, scrollable_nodes)

    def get_annotated_screenshot(
        self, nodes: list[TreeElementNode], scale: float = 1.0
    ) -> Image.Image:
        
        # ============================================================================
        # スクリーンショットを取った後、パディングを加えて画像として返す
        # ============================================================================

        # スクリーンショットを取得
        screenshot = self.desktop.get_screenshot()
        sleep(0.10)

        original_width = screenshot.width
        original_height = screenshot.height

        scaled_width = int(original_width * scale)
        scaled_height = int(original_height * scale)
        screenshot = screenshot.resize(
            (scaled_width, scaled_height), Image.Resampling.LANCZOS
        )

        # パディングを加えたスクリーンショットの画像を作成
        padding = 5
        width = int(screenshot.width + (1.5 * padding))
        height = int(screenshot.height + (1.5 * padding))
        padded_screenshot = Image.new("RGB", (width, height), color=(255, 255, 255))
        padded_screenshot.paste(screenshot, (padding, padding))

        draw = ImageDraw.Draw(padded_screenshot)
        font_size = 12
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        def get_random_color():
            return "#{:06x}".format(random.randint(0, 0xFFFFFF))

        def draw_annotation(label, node: TreeElementNode):
            box = node.bounding_box
            color = get_random_color()

            # Scale and pad the bounding box coordinates
            adjusted_box = (
                int(box.left * scale) + padding,
                int(box.top * scale) + padding,
                int(box.right * scale) + padding,
                int(box.bottom * scale) + padding,
            )
            # スクリーンの境界線を描画
            draw.rectangle(adjusted_box, outline=color, width=2)

            # ラベルのサイズ
            label_width = draw.textlength(str(label), font=font)
            label_height = font_size
            left, top, right, bottom = adjusted_box

            # ラベルの位置
            label_x1 = right - label_width
            label_y1 = top - label_height - 4
            label_x2 = label_x1 + label_width
            label_y2 = label_y1 + label_height + 4

            # ラベルの背景とテキストを描画
            draw.rectangle([(label_x1, label_y1), (label_x2, label_y2)], fill=color)
            draw.text(
                (label_x1 + 2, label_y1 + 2),
                str(label),
                fill=(255, 255, 255),
                font=font,
            )

        # 並列でアノテーションを描画
        with ThreadPoolExecutor() as executor:
            executor.map(draw_annotation, range(len(nodes)), nodes)
        return padded_screenshot
