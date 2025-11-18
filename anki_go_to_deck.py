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
    leaf_name = deck_name.split("::")[-1]
    QApplication.clipboard().setText(leaf_name)

    simulate_key(
        browser, 
        Qt.Key.Key_F, 
        Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
    )

    def step_clear_paste_enter():
        focus_widget = QApplication.focusWidget()
        
        if focus_widget:
            simulate_key(
                focus_widget, 
                Qt.Key.Key_A, 
                Qt.KeyboardModifier.ControlModifier
            )
            
            simulate_key(focus_widget, Qt.Key.Key_Backspace)
            
            simulate_key(
                focus_widget, 
                Qt.Key.Key_V, 
                Qt.KeyboardModifier.ControlModifier
            )
            
            QTimer.singleShot(50, lambda: simulate_key(focus_widget, Qt.Key.Key_Return))

    QTimer.singleShot(150, step_clear_paste_enter)

def filter_by_card_deck(browser):
    cids = browser.selectedCards()
    if not cids:
        return
    
    card = mw.col.get_card(cids[0])
    deck_name = mw.col.decks.name(card.did)
    
    browser.setFilter(f'deck:"{deck_name}"')
    
    is_legacy = expand_and_select_legacy(browser, deck_name)
    
    if not is_legacy:
        filter_sidebar_modern_keyboard(browser, deck_name)

def on_context_menu(browser, menu):
    action = menu.addAction("Go to Deck")
    action.triggered.connect(lambda: filter_by_card_deck(browser))

browser_will_show_context_menu.append(on_context_menu)