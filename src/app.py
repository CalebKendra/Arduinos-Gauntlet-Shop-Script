from __future__ import annotations

import csv
import random
import re
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSpacerItem,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from shop import shop as shop_logic


SCRIPT_DIR = Path(__file__).resolve().parent
BOONS_CSV_PATH = SCRIPT_DIR / "boons" / "boons.csv"


# Change this from 1 to 20 to bias the shop toward weaker or stronger items.
CHARACTER_LEVEL = 2
CHARACTER_TYPE = "Martial"
MAX_LEVEL = 10

# Shared shop tuning/config values are sourced from shop.py to avoid duplication.
DEBUG_MODE = shop_logic.DEBUG_MODE
TARGET_ITEMVALUE_CONCENTRATION = shop_logic.TARGET_ITEMVALUE_CONCENTRATION
CSV_CONFIGS = shop_logic.CSV_CONFIGS

APP_STYLE = """
QMainWindow {
    background: #050806;
}

QWidget {
    background: #050806;
    color: #f5fff7;
    font-family: "Bahnschrift", "Segoe UI", sans-serif;
    font-size: 11pt;
}

QLabel {
    background: transparent;
}

QTabWidget::pane {
    border: 1px solid #1f3d2b;
    border-radius: 8px;
    top: -1px;
    background: #0a120d;
}

QTabBar::tab {
    background: #0f1b14;
    color: #d8ebdd;
    padding: 10px 18px;
    border: 1px solid #1f3d2b;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    min-width: 110px;
    font-weight: 600;
}

QTabBar::tab:selected {
    color: #ffffff;
    background: #1a3a2a;
}

QLabel#SectionTitle {
    font-size: 17pt;
    font-weight: 700;
    color: #ffffff;
    padding: 4px 0px;
}

QLabel#SectionSubtitle {
    font-size: 10pt;
    color: #a6c5b0;
    padding-bottom: 8px;
}

QLabel#TokenPill {
    background: #06110b;
    border: 2px solid #57d38c;
    color: #f4fff8;
    border-radius: 18px;
    padding: 8px 16px;
    font-weight: 900;
    font-size: 12.5pt;
    letter-spacing: 1px;
}

QGroupBox {
    margin-top: 16px;
    border: 1px solid #244833;
    border-radius: 10px;
    background: #0b1610;
    padding: 14px 10px 10px 10px;
    font-weight: 700;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 2px 10px;
    color: #e7fff0;
    background: #0b1610;
    border-radius: 6px;
    font-size: 11pt;
    font-weight: 800;
}

QGroupBox#BigSixSection {
    border: 1px solid #6f4d12;
    background: #1f1607;
}

QGroupBox#BigSixSection::title {
    color: #fff2cf;
    background: #4a3510;
}

QTableWidget#BigSixTable {
    border: 1px solid #845a15;
    background: #130d04;
    alternate-background-color: #1a1207;
    selection-background-color: #6f4d12;
}

QTableWidget#BigSixTable QHeaderView::section {
    background: #4a3510;
    color: #fff4d9;
    border-right: 1px solid #7a5313;
}

QGroupBox#PotionsSection {
    border: 1px solid #1f5a64;
    background: #091a1e;
}

QGroupBox#PotionsSection::title {
    color: #ddf8ff;
    background: #174753;
}

QTableWidget#PotionsTable {
    border: 1px solid #2f7380;
    background: #051215;
    alternate-background-color: #08191d;
    selection-background-color: #1f5a64;
}

QTableWidget#PotionsTable QHeaderView::section {
    background: #174753;
    color: #e6faff;
    border-right: 1px solid #2a6d79;
}

QGroupBox#UniquesSection {
    border: 1px solid #5a1f4e;
    background: #1a0917;
}

QGroupBox#UniquesSection::title {
    color: #ffe0fa;
    background: #4a1a41;
}

QTableWidget#UniquesTable {
    border: 1px solid #7a2c6c;
    background: #12050f;
    alternate-background-color: #1a0a16;
    selection-background-color: #5a1f4e;
}

QTableWidget#UniquesTable QHeaderView::section {
    background: #4a1a41;
    color: #ffe8fc;
    border-right: 1px solid #743066;
}

QPushButton {
    background: #20402d;
    border: 1px solid #367552;
    border-radius: 8px;
    padding: 7px 12px;
    color: #f7fff9;
    font-weight: 600;
}

QPushButton:hover {
    background: #2a573e;
}

QPushButton:pressed {
    background: #183223;
}

QPushButton#PrimaryButton {
    background: #2b6e49;
    border: 1px solid #52ad79;
}

QPushButton#PrimaryButton:hover {
    background: #398f61;
}

QPushButton#DangerButton {
    background: #15201a;
    border: 1px solid #2f5640;
}

QPushButton#DangerButton:hover {
    background: #1d2e25;
}

QPushButton#ResetButton {
    background: #5c1a1a;
    border: 2px solid #c41e3a;
    color: #ffcccc;
    font-weight: 700;
}

QPushButton#ResetButton:hover {
    background: #7a2626;
    border: 2px solid #e63946;
}

QPushButton#BigSixButton {
    background: #4a3510;
    border: 1px solid #7f5a16;
    color: #fff5dd;
}

QPushButton#BigSixButton:hover {
    background: #604718;
}

QPushButton#PotionsButton {
    background: #174753;
    border: 1px solid #2e7481;
    color: #e9fbff;
}

QPushButton#PotionsButton:hover {
    background: #205c6a;
}

QPushButton#UniquesButton {
    background: #4a1a41;
    border: 1px solid #7b2f6e;
    color: #ffe8fb;
}

QPushButton#UniquesButton:hover {
    background: #5e2454;
}

QTableWidget {
    background: #070e0a;
    border: 1px solid #29533a;
    border-radius: 8px;
    gridline-color: #1b3828;
    alternate-background-color: #0a140f;
    selection-background-color: #1f4d36;
    selection-color: #ffffff;
}

QHeaderView::section {
    background: #163121;
    color: #f0fff4;
    border: none;
    border-right: 1px solid #28533a;
    padding: 7px;
    font-weight: 700;
}

QComboBox, QSpinBox {
    background: #0b1510;
    border: 1px solid #2e6244;
    border-radius: 7px;
    padding: 5px 9px;
    min-height: 24px;
}

QWidget#StartRoot {
    background: #07100b;
}

QGroupBox#StartSelectorSection {
    border: 1px solid #35684c;
    background: #0a140f;
    border-radius: 12px;
    padding: 16px;
    min-height: 260px;
}

QGroupBox#StartSelectorSection::title {
    color: #e8fff0;
    background: #173423;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 11pt;
    font-weight: 800;
}

QPushButton#StartSquareButton {
    min-width: 150px;
    min-height: 150px;
    max-width: 150px;
    max-height: 150px;
    border-radius: 12px;
    border: 2px solid #2d6c4a;
    background: #123222;
    color: #f2fff7;
    font-size: 12pt;
    font-weight: 800;
    padding: 10px;
}

QPushButton#StartSquareButton:hover {
    background: #184630;
}

QPushButton#StartTypeButton {
    min-width: 150px;
    min-height: 150px;
    max-width: 150px;
    max-height: 150px;
    border-radius: 12px;
    border: 2px solid #2d6c4a;
    background: #102b1d;
    color: #eafcf1;
    font-size: 12pt;
    font-weight: 800;
    padding: 10px;
}

QPushButton#StartTypeButton:checked {
    background: #2b7b53;
    border: 2px solid #6be0a0;
    color: #ffffff;
}

QLabel#StartValueLabel {
    font-size: 16pt;
    font-weight: 900;
    color: #ffffff;
    padding: 6px 12px;
}

QGroupBox#StartInventorySection {
    border: 1px solid #355e49;
    background: #0b1510;
    border-radius: 12px;
    padding: 16px;
}

QGroupBox#StartInventorySection::title {
    color: #e8fff0;
    background: #173423;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 11pt;
    font-weight: 800;
}

QListWidget#InventoryList {
    background: #07100b;
    border: 1px solid #2f5f44;
    border-radius: 8px;
    color: #f0fff4;
    padding: 6px;
}

QListWidget#InventoryList::item {
    padding: 6px;
}

QWidget#BoonsRoot {
    background: #07100b;
}

QFrame#BoonCard {
    background: #0f1f17;
    border: 2px solid #2c6848;
    border-radius: 12px;
}

QFrame#BoonCard[selected="true"] {
    background: #1a3d2b;
    border: 2px solid #6be0a0;
}

QLabel#BoonCardTitle {
    font-size: 15pt;
    font-weight: 800;
    color: #ffffff;
}

QLabel#BoonCardBuff {
    color: #75e89f;
    font-weight: 700;
}

QLabel#BoonCardDebuff {
    color: #ff8b8b;
    font-weight: 700;
}
"""

class ShopTab(QWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__()
        self.main_window = main_window
        self.tokens = 10
        self.character_level = int(CHARACTER_LEVEL)
        self.current_offers: dict[str, list[dict]] = {}
        self.tables_by_label: dict[str, QTableWidget] = {}

        self.token_label = QLabel()
        self.token_label.setObjectName("TokenPill")
        self.token_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.level_label = QLabel()
        self.level_label.setObjectName("SectionSubtitle")
        self.level_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.reroll_button = QPushButton("Reroll Shop (-1 Token)")
        self.reroll_button.setObjectName("DangerButton")
        self.reroll_button.clicked.connect(self.reroll_shop)

        self.finish_button = QPushButton("Finish Shopping")
        self.finish_button.setObjectName("PrimaryButton")
        self.finish_button.clicked.connect(self.finish_shopping)

        top_row = QHBoxLayout()
        top_row.addWidget(self.token_label)
        top_row.addWidget(self.level_label)
        top_row.addStretch(1)
        top_row.addWidget(self.reroll_button)
        top_row.addWidget(self.finish_button)

        root_layout = QVBoxLayout(self)

        title = QLabel("Shop Forge")
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Generate rotating offers, spend tokens, and reroll the market.")
        subtitle.setObjectName("SectionSubtitle")
        root_layout.addWidget(title)
        root_layout.addWidget(subtitle)

        root_layout.addLayout(top_row)

        # Inventory section for selling items
        inventory_section = QGroupBox("Purchased Items (Sell Back)")
        inventory_section.setObjectName("StartInventorySection")
        inventory_layout = QVBoxLayout(inventory_section)
        
        self.purchased_items_list = QListWidget()
        self.purchased_items_list.setObjectName("InventoryList")
        self.purchased_items_list.setMaximumHeight(120)
        
        sell_button_row = QHBoxLayout()
        sell_button_row.addStretch(1)
        self.sell_selected_button = QPushButton("Sell Selected Item")
        self.sell_selected_button.setObjectName("DangerButton")
        self.sell_selected_button.clicked.connect(self.sell_selected_from_inventory)
        sell_button_row.addWidget(self.sell_selected_button)
        sell_button_row.addStretch(1)
        
        inventory_layout.addWidget(self.purchased_items_list)
        inventory_layout.addLayout(sell_button_row)
        
        self.inventory_section = inventory_section
        self.shop_sections: dict[str, QGroupBox] = {}

        for config in CSV_CONFIGS:
            label = str(config["label"])
            section = QGroupBox(label)
            section.setObjectName(self._section_object_name(label))
            section_layout = QVBoxLayout(section)

            table = QTableWidget(0, len(self._shop_table_headers()))
            table.setObjectName(self._table_object_name(label))
            table.setHorizontalHeaderLabels(self._shop_table_headers())
            table.horizontalHeader().setStretchLastSection(True)
            table.verticalHeader().setDefaultSectionSize(34)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.SingleSelection)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setAlternatingRowColors(True)

            buy_button = QPushButton(f"Buy Selected From {label}")
            buy_button.setObjectName(self._buy_button_object_name(label))
            buy_button.clicked.connect(
                lambda _checked=False, section_label=label: self.buy_selected(section_label)
            )

            section_layout.addWidget(table)
            section_layout.addWidget(buy_button)

            self.tables_by_label[label] = table
            self.shop_sections[label] = section

        # Create 2x2 grid layout for shop sections
        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)
        
        # Top-left: Big Six
        grid_layout.addWidget(self.shop_sections.get("Big Six"), 0, 0)
        # Top-right: Potions, Scrolls
        grid_layout.addWidget(self.shop_sections.get("Potions, Scrolls, and Temporary Tools"), 0, 1)
        # Bottom-left: Uniques
        grid_layout.addWidget(self.shop_sections.get("Uniques"), 1, 0)
        # Bottom-right: Purchased Items
        grid_layout.addWidget(self.inventory_section, 1, 1)

        root_layout.addLayout(grid_layout)
        root_layout.addStretch(1)
        self.update_token_label()
        self.update_level_label()
        self.generate_shop()

    def _shop_table_headers(self) -> list[str]:
        if DEBUG_MODE:
            return ["Name", "Group", "CL", "ItemValue", "Tokens", "Description"]
        return ["Name", "Group", "Tokens", "Description"]

    def _section_object_name(self, label: str) -> str:
        if label == "Big Six":
            return "BigSixSection"
        if label == "Potions, Scrolls, and Temporary Tools":
            return "PotionsSection"
        if label == "Uniques":
            return "UniquesSection"
        return ""

    def _table_object_name(self, label: str) -> str:
        if label == "Big Six":
            return "BigSixTable"
        if label == "Potions, Scrolls, and Temporary Tools":
            return "PotionsTable"
        if label == "Uniques":
            return "UniquesTable"
        return ""

    def _buy_button_object_name(self, label: str) -> str:
        if label == "Big Six":
            return "BigSixButton"
        if label == "Potions, Scrolls, and Temporary Tools":
            return "PotionsButton"
        if label == "Uniques":
            return "UniquesButton"
        return ""

    def update_token_label(self) -> None:
        self.token_label.setText(f"TOKEN BANK  {self.tokens}")
        self._refresh_all_row_states()

    def update_level_label(self) -> None:
        self.level_label.setText(f"Level {self.character_level}")

    def set_character_level(self, level: int) -> None:
        self.character_level = max(1, min(MAX_LEVEL, int(level)))
        self.update_level_label()
        self.generate_shop()

    def start_new_shop_session(self) -> None:
        # Every new shop visit starts with a fresh token bank + retained tokens
        self.tokens = 10 + self.main_window.retained_tokens
        self.main_window.retained_tokens = 0
        self.update_token_label()
        self.update_purchased_items_list()
        self.generate_shop()

    def reset_tokens(self) -> None:
        self.tokens = 10
        self.update_token_label()

    def reroll_shop(self) -> None:
        if self.tokens < 1:
            QMessageBox.warning(self, "Not Enough Tokens", "You need 1 token to reroll.")
            return
        self.tokens -= 1
        self.update_token_label()
        self.generate_shop()

    def finish_shopping(self) -> None:
        # Retain half of unspent tokens, rounded down
        retained = self.tokens // 2
        self.main_window.retained_tokens += retained
        
        # Check if already at max level
        if self.character_level >= MAX_LEVEL:
            # Completing shopping at max level ends progression; future attempts are blocked on Start.
            self.main_window.has_completed_max_level_run = True
            self.main_window.mark_run_completed()
            self.main_window.tabs.setCurrentIndex(self.main_window.START_TAB_INDEX)
            return
        # Increment level for next run, capped at MAX_LEVEL
        if self.character_level < MAX_LEVEL:
            self.character_level += 1
        self.main_window.mark_run_completed()
        self.main_window.tabs.setCurrentIndex(self.main_window.START_TAB_INDEX)

    def generate_shop(self) -> None:
        character_level = self.character_level
        target_value = shop_logic.level_to_target_value(character_level)

        for config in CSV_CONFIGS:
            label = str(config["label"])
            table = self.tables_by_label[label]
            table.setRowCount(0)
            self.current_offers[label] = []

            csv_path = Path(config["path"])
            if not csv_path.exists():
                continue

            frame = pd.read_csv(csv_path)
            if "ItemValue" not in frame.columns:
                continue

            range_width = shop_logic.level_to_range_width(
                character_level,
                config["range_width"],
                config["range_growth_per_level"],
                config["range_max"],
            )

            sampled_items = shop_logic.weighted_sample(
                frame,
                target_value,
                range_width=range_width,
                scroll_weight_multiplier=config.get("scroll_weight_multiplier", 1.0),
                potion_weight_multiplier=config.get("potion_weight_multiplier", 1.0),
                armor_special_modifier=config.get("armor_special_modifier", 1.0),
                weapon_special_modifier=config.get("weapon_special_modifier", 1.0),
                target_itemvalue_concentration=TARGET_ITEMVALUE_CONCENTRATION,
                count=config["items_per_section"],
            )

            offers: list[dict] = []
            for _, row in sampled_items.iterrows():
                item_value = float(pd.to_numeric(row.get("ItemValue"), errors="coerce"))
                item_group = shop_logic.clean_description(row.get("Group", ""))
                token_cost = shop_logic.token_cost_for_item(
                    item_value,
                    target_value,
                    range_width,
                    character_level,
                    config.get("token_csv_modifier", 1.0),
                    config.get("token_level_cost_scale", 1.0),
                    config.get("token_shift_above_target", 9.0),
                    config.get("token_shift_below_target", 2.0),
                    item_group,
                    config.get("token_special_modifiers"),
                )

                offers.append(
                    {
                        "Name": shop_logic.clean_description(row.get("Name", "")),
                        "Group": item_group,
                        "CL": shop_logic.clean_description(row.get("CL", "")),
                        "ItemValue": item_value,
                        "Description": shop_logic.clean_description(row.get("Description", "")),
                        "Tokens": token_cost,
                        "Purchased": False,
                    }
                )

            self.current_offers[label] = offers
            self._populate_shop_table(label)

    def _populate_shop_table(self, label: str) -> None:
        table = self.tables_by_label[label]
        offers = self.current_offers.get(label, [])
        table.setRowCount(len(offers))

        for row_index, offer in enumerate(offers):
            if DEBUG_MODE:
                row_values = [
                    offer["Name"],
                    offer["Group"],
                    str(offer["CL"]),
                    f"{float(offer['ItemValue']):.2f}",
                    str(offer["Tokens"]),
                    offer["Description"],
                ]
            else:
                row_values = [
                    offer["Name"],
                    offer["Group"],
                    str(offer["Tokens"]),
                    offer["Description"],
                ]
            for col_index, value in enumerate(row_values):
                table.setItem(row_index, col_index, QTableWidgetItem(value))

        self._refresh_row_states(label)
        self._fit_table_height_to_rows(table)
        table.resizeColumnsToContents()

    def _fit_table_height_to_rows(self, table: QTableWidget) -> None:
        # Keep each table tall enough for all rows with a little breathing room.
        row_count = table.rowCount()
        content_height = table.horizontalHeader().height()
        for row_index in range(row_count):
            content_height += table.rowHeight(row_index)

        total_height = content_height + (table.frameWidth() * 2) + 16
        table.setMinimumHeight(total_height)
        table.setMaximumHeight(total_height)

    def _refresh_all_row_states(self) -> None:
        for label in self.tables_by_label:
            self._refresh_row_states(label)

    def _refresh_row_states(self, label: str) -> None:
        table = self.tables_by_label.get(label)
        offers = self.current_offers.get(label, [])
        if table is None:
            return

        for row_index, offer in enumerate(offers):
            purchased = bool(offer.get("Purchased", False))
            unaffordable = int(offer.get("Tokens", 0)) > self.tokens

            for col_index in range(table.columnCount()):
                item = table.item(row_index, col_index)
                if item is None:
                    continue

                if purchased:
                    item.setFlags(Qt.ItemIsEnabled)
                    item.setForeground(QColor("#7f8e86"))
                    item.setBackground(QColor("#0f1813"))
                else:
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item.setBackground(QColor(0, 0, 0, 0))
                    if unaffordable:
                        item.setForeground(QColor("#ff7373"))
                    else:
                        item.setForeground(QColor("#f5fff7"))

    def buy_selected(self, label: str) -> None:
        table = self.tables_by_label[label]
        selected_row = table.currentRow()
        if selected_row < 0:
            return

        offers = self.current_offers.get(label, [])
        if selected_row >= len(offers):
            return

        offer = offers[selected_row]
        if bool(offer.get("Purchased", False)):
            return

        cost = int(offer["Tokens"])
        if cost > self.tokens:
            return

        self.tokens -= cost
        self.update_token_label()
        offer["Purchased"] = True
        self.main_window.record_purchased_item(label, offer)
        self._refresh_all_row_states()
        self.update_purchased_items_list()

    def update_purchased_items_list(self) -> None:
        """Update the list of items available to sell."""
        self.purchased_items_list.clear()
        for i, item in enumerate(self.main_window.inventory_items):
            item_name = str(item.get("Name", "Unknown Item"))
            token_value = item.get("Tokens", 0)
            sell_price = token_value // 2
            self.purchased_items_list.addItem(
                QListWidgetItem(f"{item_name} (Sell for {sell_price} tokens)")
            )

    def sell_selected_from_inventory(self) -> None:
        """Sell the selected item from the purchased items list."""
        selected_row = self.purchased_items_list.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to sell.")
            return

        if selected_row >= len(self.main_window.inventory_items):
            return

        item = self.main_window.inventory_items[selected_row]
        item_name = str(item.get("Name", "Unknown Item"))
        token_value = item.get("Tokens", 0)
        sell_price = token_value // 2

        # Add tokens back
        self.tokens += sell_price
        self.update_token_label()

        # Remove from inventory
        self.main_window.inventory_items.pop(selected_row)

        # Update the list
        self.update_purchased_items_list()

        QMessageBox.information(
            self,
            "Item Sold",
            f"Sold {item_name} for {sell_price} tokens.\n\nTokens: {self.tokens}",
        )


class BoonCard(QFrame):
    def __init__(self, boon: dict[str, str], on_select) -> None:
        super().__init__()
        self.boon = boon
        self.on_select = on_select
        self.setObjectName("BoonCard")
        self.setProperty("selected", False)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(320, 280)
        self.setMaximumWidth(360)

        title_label = QLabel(boon["BoonName"])
        title_label.setObjectName("BoonCardTitle")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignHCenter)

        buff_label = QLabel(boon["Buff"])
        buff_label.setObjectName("BoonCardBuff")
        buff_label.setWordWrap(True)

        debuff_label = QLabel(boon["Debuff"])
        debuff_label.setObjectName("BoonCardDebuff")
        debuff_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(title_label)
        layout.addSpacing(8)
        layout.addWidget(buff_label)
        layout.addSpacing(6)
        layout.addWidget(debuff_label)
        layout.addStretch(1)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event) -> None:
        if callable(self.on_select):
            self.on_select(self)
        super().mousePressEvent(event)


class BoonsTab(QWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__()
        self.main_window = main_window
        self.boons = self.load_boons()
        self.character_type = CHARACTER_TYPE.strip().title()
        self.current_rolled_boons: list[dict[str, str]] = []
        self.selected_boon: dict[str, str] | None = None
        self.boon_cards: list[BoonCard] = []

        self.setObjectName("BoonsRoot")

        self.current_type_label = QLabel()
        self.current_type_label.setObjectName("SectionSubtitle")
        self.current_type_label.setAlignment(Qt.AlignHCenter)

        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(20)
        self.cards_row.addStretch(1)
        self.cards_row.addStretch(1)

        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setSpacing(16)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.addWidget(self.current_type_label)
        center_layout.addLayout(self.cards_row)

        self.confirm_button = QPushButton("Confirm Boon")
        self.confirm_button.setObjectName("PrimaryButton")
        self.confirm_button.setMinimumHeight(44)
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self.confirm_boon)

        actions = QHBoxLayout()
        actions.addStretch(1)
        actions.addWidget(self.confirm_button)
        actions.addStretch(1)

        layout = QVBoxLayout(self)
        title = QLabel("Boon Crucible")
        title.setObjectName("SectionTitle")
        title.setAlignment(Qt.AlignHCenter)
        subtitle = QLabel("Choose your path and roll three fate-touched boons.")
        subtitle.setObjectName("SectionSubtitle")
        subtitle.setAlignment(Qt.AlignHCenter)
        layout.addStretch(2)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(center_panel)
        layout.addSpacing(10)
        layout.addLayout(actions)
        layout.addStretch(3)

        self.set_character_type(CHARACTER_TYPE)

    def load_boons(self) -> list[dict[str, str]]:
        if not BOONS_CSV_PATH.exists():
            return []

        with BOONS_CSV_PATH.open("r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            cleaned_rows: list[dict[str, str]] = []
            for row in reader:
                boon_name = (row.get("BoonName") or "").strip()
                boon_type = (row.get("Type") or "").strip().title()
                buff = (row.get("Buff") or "").strip()
                debuff = (row.get("Debuff") or "").strip()
                if not boon_name or boon_type not in {"Martial", "Caster", "General"}:
                    continue
                cleaned_rows.append(
                    {
                        "BoonName": boon_name,
                        "Type": boon_type,
                        "Buff": buff,
                        "Debuff": debuff,
                    }
                )
            return cleaned_rows

    def set_character_type(self, character_type: str) -> None:
        normalized = character_type.strip().title()
        if normalized not in {"Martial", "Caster"}:
            normalized = "Martial"
        self.character_type = normalized
        self.current_type_label.setText(f"Current Type: {self.character_type}")
        self.prepare_boons()

    def prepare_boons(self) -> None:
        allowed_types = {self.character_type, "General"}

        pool = [boon for boon in self.boons if boon["Type"] in allowed_types]
        
        # Filter out boons already taken in this run
        taken_boon_names = {boon["BoonName"] for boon in self.main_window.inventory_boons}
        pool = [boon for boon in pool if boon["BoonName"] not in taken_boon_names]
        
        if len(pool) < 3:
            self.current_rolled_boons = []
            self._render_boon_cards()
            return

        self.current_rolled_boons = random.sample(pool, 3)
        self._render_boon_cards()

    def _render_boon_cards(self) -> None:
        while self.cards_row.count() > 0:
            item = self.cards_row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.cards_row.addStretch(1)
        self.selected_boon = None
        self.confirm_button.setEnabled(False)
        self.boon_cards = []

        for boon in self.current_rolled_boons:
            card = BoonCard(boon, self._handle_card_selected)
            self.boon_cards.append(card)
            self.cards_row.addWidget(card)

        self.cards_row.addStretch(1)

    def _handle_card_selected(self, selected_card: BoonCard) -> None:
        for card in self.boon_cards:
            card.set_selected(card is selected_card)
        self.selected_boon = selected_card.boon
        self.confirm_button.setEnabled(True)

    def confirm_boon(self) -> None:
        if self.selected_boon is None:
            return
        self.main_window.record_selected_boon(self.selected_boon)
        self.main_window.shop_tab.start_new_shop_session()
        self.main_window.tabs.setCurrentIndex(self.main_window.SHOP_TAB_INDEX)


class StartTab(QWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__()
        self.main_window = main_window
        self.current_level = int(CHARACTER_LEVEL)
        self.selected_type = CHARACTER_TYPE.strip().title()

        self.setObjectName("StartRoot")

        title = QLabel("Arduino's Gauntlet")
        title.setObjectName("SectionTitle")
        title.setAlignment(Qt.AlignHCenter)
        subtitle = QLabel("Begin shopping and rolling boons for your next combat.")
        subtitle.setObjectName("SectionSubtitle")
        subtitle.setAlignment(Qt.AlignHCenter)

        self.reset_button = QPushButton("RESET RUN")
        self.reset_button.setObjectName("ResetButton")
        self.reset_button.setMaximumWidth(120)
        self.reset_button.clicked.connect(self.on_reset_run_clicked)

        reset_row = QHBoxLayout()
        reset_row.addStretch(1)
        reset_row.addWidget(self.reset_button)
        reset_row.setContentsMargins(0, 0, 20, 0)

        title_row = QHBoxLayout()
        title_row.addStretch(1)
        title_row.addWidget(title)
        title_row.addStretch(1)

        self.level_display_label = QLabel()
        self.level_display_label.setObjectName("StartValueLabel")
        self.level_display_label.setAlignment(Qt.AlignHCenter)

        self.martial_button = QPushButton("MARTIAL")
        self.martial_button.setObjectName("StartTypeButton")
        self.martial_button.setCheckable(True)
        self.martial_button.clicked.connect(lambda: self.select_type("Martial"))

        self.caster_button = QPushButton("CASTER")
        self.caster_button.setObjectName("StartTypeButton")
        self.caster_button.setCheckable(True)
        self.caster_button.clicked.connect(lambda: self.select_type("Caster"))

        self.type_value_label = QLabel()
        self.type_value_label.setObjectName("StartValueLabel")
        self.type_value_label.setAlignment(Qt.AlignHCenter)

        type_section = QGroupBox("Type")
        type_section.setObjectName("StartSelectorSection")
        type_buttons = QHBoxLayout()
        type_buttons.addWidget(self.martial_button)
        type_buttons.addWidget(self.caster_button)
        type_layout = QVBoxLayout(type_section)
        type_layout.addWidget(self.type_value_label)
        type_layout.addStretch(1)
        type_layout.addLayout(type_buttons)
        type_layout.addStretch(1)

        self.type_section = type_section

        selectors_col = QVBoxLayout()
        selectors_col.setSpacing(16)
        selectors_col.addWidget(self.level_display_label)
        selectors_col.addWidget(self.type_section)

        selectors_row = QHBoxLayout()
        selectors_row.setSpacing(24)
        selectors_row.addStretch(1)
        selectors_row.addLayout(selectors_col)
        selectors_row.addStretch(1)

        apply_button = QPushButton("Continue to Boons")
        apply_button.setObjectName("PrimaryButton")
        apply_button.clicked.connect(self.apply_settings)
        apply_button.setMinimumHeight(44)

        actions = QHBoxLayout()
        actions.addStretch(1)
        actions.addWidget(apply_button)
        actions.addStretch(1)

        self.inventory_section = QGroupBox("Inventory")
        self.inventory_section.setObjectName("StartInventorySection")
        self.inventory_section.setVisible(False)
        self.inventory_section.setMinimumHeight(420)

        self.boon_inventory_list = QListWidget()
        self.boon_inventory_list.setObjectName("InventoryList")
        self.big_six_inventory_list = QListWidget()
        self.big_six_inventory_list.setObjectName("InventoryList")
        self.item_inventory_list = QListWidget()
        self.item_inventory_list.setObjectName("InventoryList")

        boon_column = QVBoxLayout()
        boon_title = QLabel("Boons Taken")
        boon_title.setObjectName("SectionSubtitle")
        boon_column.addWidget(boon_title)
        boon_column.addWidget(self.boon_inventory_list)

        item_column = QVBoxLayout()
        big_six_title = QLabel("Big 6 Summary")
        big_six_title.setObjectName("SectionSubtitle")
        item_column.addWidget(big_six_title)
        item_column.addWidget(self.big_six_inventory_list)
        item_title = QLabel("Items Purchased")
        item_title.setObjectName("SectionSubtitle")
        item_column.addWidget(item_title)
        item_column.addWidget(self.item_inventory_list)

        inventory_layout = QHBoxLayout(self.inventory_section)
        inventory_layout.setSpacing(16)
        inventory_layout.addLayout(boon_column)
        inventory_layout.addLayout(item_column)

        self.inventory_offset_spacer = QSpacerItem(
            0,
            0,
            QSizePolicy.Minimum,
            QSizePolicy.Fixed,
        )

        self.root_layout = QVBoxLayout(self)
        self.root_layout.addStretch(1)
        self.root_layout.addItem(self.inventory_offset_spacer)
        self.root_layout.addLayout(reset_row)
        self.root_layout.addLayout(title_row)
        self.root_layout.addWidget(subtitle)
        self.root_layout.addSpacing(10)
        self.root_layout.addLayout(selectors_row)
        self.root_layout.addSpacing(10)
        self.root_layout.addLayout(actions)
        self.root_layout.addSpacing(12)
        self.root_layout.addWidget(self.inventory_section, 1)
        self.root_layout.addStretch(1)

        self.refresh_start_display()

    def select_type(self, character_type: str) -> None:
        normalized = character_type.strip().title()
        if normalized not in {"Martial", "Caster"}:
            return
        self.selected_type = normalized
        self.refresh_start_display()

    def refresh_start_display(self) -> None:
        # Show level and type when past starting level, just level at start
        level_text = f"Level {self.current_level}"
        if self.current_level > CHARACTER_LEVEL:
            level_text += f" - {self.selected_type}"
        # Add retained tokens info if any
        if self.main_window.retained_tokens > 0:
            level_text += f" | +{self.main_window.retained_tokens} Tokens"
        self.level_display_label.setText(level_text)
        self.type_value_label.setText(f"Type {self.selected_type}")
        # Only allow type selection at starting level
        can_select_type = self.current_level == CHARACTER_LEVEL
        self.type_section.setVisible(can_select_type)
        self.martial_button.setEnabled(can_select_type)
        self.caster_button.setEnabled(can_select_type)
        self.martial_button.setChecked(self.selected_type == "Martial")
        self.caster_button.setChecked(self.selected_type == "Caster")

    def apply_settings(self) -> None:
        if self.current_level >= MAX_LEVEL and self.main_window.has_completed_max_level_run:
            QMessageBox.information(
                self,
                "Max Level Reached",
                f"You already completed your level {MAX_LEVEL} run. Reset to start a new run.",
            )
            return
        self.main_window.shop_tab.set_character_level(self.current_level)
        self.main_window.boons_tab.set_character_type(self.selected_type)
        self.main_window.tabs.setCurrentIndex(self.main_window.BOONS_TAB_INDEX)

    def update_level_display(self, level: int) -> None:
        self.current_level = level
        self.refresh_start_display()
        # Disable type selection when level changes from starting level
        can_select_type = self.current_level == CHARACTER_LEVEL
        self.martial_button.setEnabled(can_select_type)
        self.caster_button.setEnabled(can_select_type)

    def on_reset_run_clicked(self) -> None:
        choice = QMessageBox.warning(
            self,
            "Reset Run",
            "Are you sure you want to reset your run? All boons and items will be lost and you will start back at level 2.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if choice == QMessageBox.Yes:
            self.main_window.reset_run()

    def update_inventory_panel(
        self,
        boons_taken: list[dict[str, str]],
        items_purchased: list[dict[str, str]],
        visible: bool,
    ) -> None:
        self.inventory_section.setVisible(visible)
        self.inventory_offset_spacer.changeSize(
            0,
            24 if visible else 0,
            QSizePolicy.Minimum,
            QSizePolicy.Fixed,
        )
        self.root_layout.invalidate()
        if not visible:
            return

        self.boon_inventory_list.clear()
        self.boon_inventory_list.setUniformItemSizes(False)
        list_width = self.boon_inventory_list.viewport().width() if self.boon_inventory_list.viewport().width() > 0 else 280
        
        for boon in boons_taken:
            boon_name = boon.get("BoonName", "Unknown Boon")
            boon_buff = boon.get("Buff", "")
            boon_debuff = boon.get("Debuff", "")
            
            # Create container widget with fixed width for proper text wrapping
            container = QWidget()
            container.setFixedWidth(list_width - 20)
            container.setStyleSheet("background: transparent;")
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(6, 6, 6, 6)
            container_layout.setSpacing(2)
            
            # Create a label with HTML for colored text
            boon_label = QLabel()
            boon_label.setText(
                f"{boon_name}<br/><span style='color: #00FF00;'>+ {boon_buff}</span><br/><span style='color: #FF0000;'>- {boon_debuff}</span>"
            )
            boon_label.setWordWrap(True)
            boon_label.setFixedWidth(list_width - 32)
            container_layout.addWidget(boon_label)
            
            # Add item and set the container as its widget
            item = QListWidgetItem()
            self.boon_inventory_list.addItem(item)
            self.boon_inventory_list.setItemWidget(item, container)
            # Calculate height from rendered wrapped text so entries never clip.
            boon_label.adjustSize()
            required_height = boon_label.sizeHint().height() + 30
            item.setSizeHint(QSize(list_width - 20, required_height))

        self.item_inventory_list.clear()
        for item in items_purchased:
            item_name = str(item.get("Name", "Unknown Item"))
            item_source = str(item.get("Section", ""))
            self.item_inventory_list.addItem(
                QListWidgetItem(f"{item_name} ({item_source})" if item_source else item_name)
            )

        self.big_six_inventory_list.clear()
        big_six_totals = self._compute_big_six_bonus_totals(items_purchased)
        if not big_six_totals:
            self.big_six_inventory_list.addItem(QListWidgetItem("No Big 6 bonuses yet"))
        else:
            for label, value in big_six_totals.items():
                self.big_six_inventory_list.addItem(QListWidgetItem(f"{label}: +{value}"))

    def _extract_bonus_value(self, item_name: str) -> int:
        match = re.search(r"\+(\d+)", item_name)
        if not match:
            return 0
        return int(match.group(1))

    def _compute_big_six_bonus_totals(
        self,
        items_purchased: list[dict[str, str]],
    ) -> dict[str, int]:
        totals: dict[str, int] = {
            "Cloak Resistance": 0,
            "Ring Protection": 0,
            "Amulet Natural Armor": 0,
            "Magic Weapon": 0,
            "Magic Armor": 0,
        }

        for item in items_purchased:
            item_name = str(item.get("Name", ""))
            item_source = str(item.get("Section", ""))

            if item_source != "Big Six":
                continue

            bonus_value = self._extract_bonus_value(item_name)
            if bonus_value <= 0:
                continue

            lowered_name = item_name.lower()
            if "cloak of resistance" in lowered_name:
                totals["Cloak Resistance"] += bonus_value
            elif "ring of protection" in lowered_name:
                totals["Ring Protection"] += bonus_value
            elif "amulet of natural armor" in lowered_name:
                totals["Amulet Natural Armor"] += bonus_value
            elif "headband" in lowered_name:
                label = self._headband_bonus_label(lowered_name)
                totals[label] = totals.get(label, 0) + bonus_value
            elif "belt" in lowered_name:
                label = self._belt_bonus_label(lowered_name)
                totals[label] = totals.get(label, 0) + bonus_value
            elif "magic weapon" in lowered_name:
                totals["Magic Weapon"] += bonus_value
            elif "magic armor" in lowered_name:
                totals["Magic Armor"] += bonus_value

        return {key: value for key, value in totals.items() if value > 0}

    def _belt_bonus_label(self, lowered_name: str) -> str:
        if "giant strength" in lowered_name:
            return "Belt (STR)"
        if "incredible dexterity" in lowered_name:
            return "Belt (DEX)"
        if "mighty constitution" in lowered_name:
            return "Belt (CON)"
        if "physical perfection" in lowered_name:
            return "Belt (All Physical)"
        if "physical might" in lowered_name:
            return "Belt (Physical Might)"
        return "Belt (Other)"

    def _headband_bonus_label(self, lowered_name: str) -> str:
        if "vast intelligence" in lowered_name:
            return "Headband (INT)"
        if "inspired wisdom" in lowered_name:
            return "Headband (WIS)"
        if "alluring charisma" in lowered_name:
            return "Headband (CHA)"
        if "mental superiority" in lowered_name:
            return "Headband (All Mental)"
        if "mental prowess" in lowered_name:
            return "Headband (Mental Prowess)"
        return "Headband (Other)"


class MainWindow(QMainWindow):
    START_TAB_INDEX = 0
    BOONS_TAB_INDEX = 1
    SHOP_TAB_INDEX = 2

    def __init__(self) -> None:
        super().__init__()
        self.inventory_boons: list[dict[str, str]] = []
        self.inventory_items: list[dict[str, str]] = []
        self.has_completed_run = False
        self.has_completed_max_level_run = False
        self.retained_tokens: int = 0

        self.setWindowTitle("Arduino's Gauntlet")
        self.resize(1380, 1200)
        self.setMinimumHeight(1100)

        self.tabs = QTabWidget()
        self.shop_tab = ShopTab(self)
        self.boons_tab = BoonsTab(self)
        self.start_tab = StartTab(self)

        self.tabs.addTab(self.start_tab, "Start")
        self.tabs.addTab(self.boons_tab, "Boons")
        self.tabs.addTab(self.shop_tab, "Shop")
        self.tabs.tabBar().hide()
        self.tabs.setCurrentIndex(self.START_TAB_INDEX)
        self.setCentralWidget(self.tabs)
        self.start_tab.update_inventory_panel(
            self.inventory_boons,
            self.inventory_items,
            self.has_completed_run,
        )

    def record_selected_boon(self, boon: dict[str, str]) -> None:
        self.inventory_boons.append(dict(boon))

    def record_purchased_item(self, section_label: str, offer: dict[str, object]) -> None:
        self.inventory_items.append(
            {
                "Name": str(offer.get("Name", "Unknown Item")),
                "Section": section_label,
                "Tokens": int(offer.get("Tokens", 0)),
            }
        )

    def mark_run_completed(self) -> None:
        self.has_completed_run = True
        # Update level display after shop completion
        self.start_tab.update_level_display(self.shop_tab.character_level)
        self.start_tab.update_inventory_panel(
            self.inventory_boons,
            self.inventory_items,
            self.has_completed_run,
        )

    def reset_run(self) -> None:
        """Reset the entire run back to the start."""
        self.inventory_boons = []
        self.inventory_items = []
        self.has_completed_run = False
        self.has_completed_max_level_run = False
        self.retained_tokens = 0
        self.shop_tab.character_level = int(CHARACTER_LEVEL)
        self.shop_tab.update_level_label()
        self.shop_tab.generate_shop()
        self.start_tab.current_level = int(CHARACTER_LEVEL)
        self.start_tab.refresh_start_display()
        self.start_tab.update_inventory_panel(
            self.inventory_boons,
            self.inventory_items,
            self.has_completed_run,
        )


def main() -> None:
    app = QApplication([])
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
