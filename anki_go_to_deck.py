from aqt import mw
from aqt.gui_hooks import browser_will_show_context_menu
from aqt.qt import (
    QTreeWidgetItemIterator, 
    QApplication, 
    Qt, 
    QKeyEvent, 
    QEvent, 
    QTimer
)

def expand_and_select_legacy(browser, deck_name):
    try:
        tree = browser.form.searchTree
    except AttributeError:
        return False

    iterator = QTreeWidgetItemIterator(tree)
    while iterator.value():
        item = iterator.value()
        if item.text(0) == deck_name:
            parent = item.parent()
            while parent:
                parent.setExpanded(True)
                parent = parent.parent()
            
            tree.setCurrentItem(item)
            item.setSelected(True)
            tree.scrollToItem(item)
            return True
        
        iterator += 1
    
    return False

def simulate_key(widget, key, modifiers=Qt.KeyboardModifier.NoModifier):
    e_press = QKeyEvent(QEvent.Type.KeyPress, key, modifiers)
    e_release = QKeyEvent(QEvent.Type.KeyRelease, key, modifiers)
    QApplication.postEvent(widget, e_press)
    QApplication.postEvent(widget, e_release)

def filter_sidebar_modern_keyboard(browser, deck_name):
    # 1. Copy the leaf deck name to the clipboard
    leaf_name = deck_name.split("::")[-1]
    QApplication.clipboard().setText(leaf_name)

    # 2. Emulate Ctrl+Shift+F to focus the sidebar filter
    # We send the event to the browser window to trigger the global shortcut
    simulate_key(
        browser, 
        Qt.Key.Key_F, 
        Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
    )

    def step_paste_and_enter():
        # 3. Get the currently focused widget (should be the sidebar input now)
        focus_widget = QApplication.focusWidget()
        
        if focus_widget:
            # Emulate Ctrl+V (Paste)
            simulate_key(
                focus_widget, 
                Qt.Key.Key_V, 
                Qt.KeyboardModifier.ControlModifier
            )
            
            # 4. Emulate Enter after a short delay to allow paste to complete
            QTimer.singleShot(50, lambda: simulate_key(focus_widget, Qt.Key.Key_Return))

    # Wait 150ms for the Ctrl+Shift+F focus change to happen
    QTimer.singleShot(150, step_paste_and_enter)

def filter_by_card_deck(browser):
    cids = browser.selectedCards()
    if not cids:
        return
    
    card = mw.col.get_card(cids[0])
    deck_name = mw.col.decks.name(card.did)
    
    # Standard main view filter
    browser.setFilter(f'deck:"{deck_name}"')
    
    # Try Legacy method
    is_legacy = expand_and_select_legacy(browser, deck_name)
    
    # If not legacy, use Keyboard Emulation method
    if not is_legacy:
        filter_sidebar_modern_keyboard(browser, deck_name)

def on_context_menu(browser, menu):
    action = menu.addAction("Go to Deck")
    action.triggered.connect(lambda: filter_by_card_deck(browser))

browser_will_show_context_menu.append(on_context_menu)