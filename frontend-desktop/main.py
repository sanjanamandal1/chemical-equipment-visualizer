import sys
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QTableWidget, QTableWidgetItem,
    QTabWidget, QMessageBox, QScrollArea, QFrame, QGridLayout,
    QInputDialog, QLineEdit, QTextEdit
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QBrush, QPen


# Custom styled widget for gradient cards
class GradientCard(QFrame):
    def __init__(self, color1, color2, icon, title, value, parent=None):
        super().__init__(parent)
        self.color1 = color1
        self.color2 = color2
        self.setMinimumHeight(120)
        self.setMaximumHeight(150)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Icon label
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(icon_label)

        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Normal))
        title_label.setStyleSheet("color: rgba(255, 255, 255, 0.95); background: transparent;")

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        value_label.setStyleSheet("color: white; background: transparent;")

        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        text_layout.addStretch()

        layout.addLayout(text_layout)
        layout.addStretch()

        self.setLayout(layout)

        # Rounded corners
        self.setStyleSheet("""
            QFrame {
                border-radius: 15px;
                border: none;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

     
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(self.color1))
        gradient.setColorAt(1, QColor(self.color2))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)



class ModernButton(QPushButton):
    def __init__(self, text, icon="", color="#14b8a6", parent=None):
        super().__init__(parent)
        self.default_color = color
        self.hover_color = self.adjust_color(color, -15)
        self.setText(f"{icon}  {text}" if icon else text)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(45)
        self.update_style()

    def adjust_color(self, hex_color, amount):
        """Darken or lighten color"""
        color = QColor(hex_color)
        h, s, l, a = color.getHsl()
        l = max(0, min(255, l + amount))
        return QColor.fromHsl(h, s, l, a).name()

    def update_style(self, hover=False):
        color = self.hover_color if hover else self.default_color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI';
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.adjust_color(self.default_color, -30)};
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #888888;
            }}
        """)

    def enterEvent(self, event):
        self.update_style(hover=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update_style(hover=False)
        super().leaveEvent(event)


class EquipmentVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer - Teal Edition")
        self.setGeometry(100, 50, 1600, 1000)
        self.setMinimumSize(1200, 800)

        self.api_url = "http://localhost:8000/api/datasets/upload/"
        self.current_data = None

        # Set teal theme
        self.setup_theme()
        self.init_ui()

        # Add fade-in animation
        self.fade_in()

    def setup_theme(self):
        """Setup Teal & White theme"""
        palette = QPalette()

        # Teal theme colors
        palette.setColor(QPalette.Window, QColor(240, 253, 250))       # Very light teal (#F0FDFA)
        palette.setColor(QPalette.WindowText, QColor(19, 78, 74))      # Dark teal (#134E4A)
        palette.setColor(QPalette.Base, QColor(255, 255, 255))         # Pure white
        palette.setColor(QPalette.AlternateBase, QColor(204, 251, 241))  # Light teal (#CCFBF1)
        palette.setColor(QPalette.Text, QColor(19, 78, 74))            # Dark teal

        self.setPalette(palette)
        self.setFont(QFont("Segoe UI", 10))

    def fade_in(self):
        """Smooth fade-in animation on startup"""
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def init_ui(self):
        # Main central widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #F0FDFA;")  # Teal background
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # ==================== HEADER ====================
        header_container = QFrame()
        header_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #14b8a6, stop:1 #0d9488);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        header_container.setMinimumHeight(120)

        header_layout = QVBoxLayout()

        # Title
        title = QLabel("🧪 Chemical Equipment Parameter Visualizer")
        title_font = QFont("Segoe UI", 26, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: white; background: transparent;")

        subtitle = QLabel("Advanced Analytics & Visualization Platform")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet(
            "color: rgba(255, 255, 255, 0.9); background: transparent; margin-top: 5px;"
        )

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_container.setLayout(header_layout)

        main_layout.addWidget(header_container)

        # ==================== ACTION BUTTONS ====================
        button_container = QFrame()
        button_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
                border: 2px solid #99f6e4;
            }
        """)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        # Teal-themed buttons
        self.upload_btn = ModernButton("Upload CSV File", "📁", "#14b8a6")
        self.upload_btn.clicked.connect(self.upload_file)

        self.history_btn = ModernButton("View History", "📚", "#0891b2")
        self.history_btn.clicked.connect(self.show_history)

        self.pdf_btn = ModernButton("Download PDF", "📄", "#06b6d4")
        self.pdf_btn.clicked.connect(self.download_pdf)
        self.pdf_btn.setEnabled(False)

        self.refresh_btn = ModernButton("Refresh", "🔄", "#2dd4bf")
        self.refresh_btn.clicked.connect(self.refresh_data)

        # Status label
        self.status_label = QLabel("⚡ Ready to analyze data")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet("""
            color: #134E4A;
            padding: 10px 15px;
            background-color: #CCFBF1;
            border-radius: 8px;
            border-left: 4px solid #14b8a6;
        """)

        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.history_btn)
        button_layout.addWidget(self.pdf_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.status_label)

        button_container.setLayout(button_layout)
        main_layout.addWidget(button_container)

        # ==================== SUMMARY CARDS ====================
        self.cards_container = QFrame()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(15)

        # Teal-themed gradient cards
        self.card1 = GradientCard("#14b8a6", "#0d9488", "📦", "Total Equipment", "0")
        self.card2 = GradientCard("#06b6d4", "#0891b2", "💧", "Avg Flowrate", "N/A")
        self.card3 = GradientCard("#0891b2", "#0e7490", "⚡", "Avg Pressure", "N/A")
        self.card4 = GradientCard("#2dd4bf", "#14b8a6", "🌡️", "Avg Temperature", "N/A")

        self.cards_layout.addWidget(self.card1, 0, 0)
        self.cards_layout.addWidget(self.card2, 0, 1)
        self.cards_layout.addWidget(self.card3, 0, 2)
        self.cards_layout.addWidget(self.card4, 0, 3)

        self.cards_container.setLayout(self.cards_layout)
        main_layout.addWidget(self.cards_container)

        # ==================== TABS ====================
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
                border-radius: 15px;
                padding: 0px;
                border: 2px solid #99f6e4;
            }
            QTabBar::tab {
                background: #F0FDFA;
                color: #134E4A;
                padding: 12px 30px;
                margin-right: 5px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-size: 13px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: white;
                color: #0d9488;
                border-bottom: 3px solid #14b8a6;
            }
            QTabBar::tab:hover {
                background: #CCFBF1;
            }
        """)

        # Summary Tab
        self.summary_widget = QWidget()
        self.summary_widget.setStyleSheet("background: white; border-radius: 15px;")
        self.summary_layout = QVBoxLayout()
        self.summary_layout.setContentsMargins(40, 40, 40, 40)

        self.summary_label = QLabel()
        self.summary_label.setText("""
            <div style='text-align: center; padding: 60px;'>
                <h2 style='color: #134E4A; font-size: 24px; margin-bottom: 10px;'>
                    📊 No Data Available
                </h2>
                <p style='color: #0d9488; font-size: 16px;'>
                    Upload a CSV file to see comprehensive analytics and visualizations
                </p>
            </div>
        """)
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.summary_label.setTextFormat(Qt.RichText)

        self.summary_layout.addWidget(self.summary_label)
        self.summary_widget.setLayout(self.summary_layout)

        # Table Tab
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 15px;
                gridline-color: #99f6e4;
                font-size: 14px;
            }
            QHeaderView::section {
                background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
                padding: 16px;
                border: none;
                font-weight: 700;
                color: white;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 14px;
                border-bottom: 2px solid #CCFBF1;
                color: #134E4A;
                height: 45px;
            }
            QTableWidget::item:alternate-background-color {
                background-color: #F0FDFA;
            }
            QTableWidget::item:selected {
                background-color: #CCFBF1;
                color: #0d9488;
                font-weight: 600;
            }
        """)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setShowGrid(True)
        self.table_widget.verticalHeader().setDefaultSectionSize(45)

        # Charts Tab
        self.charts_widget = QWidget()
        self.charts_widget.setStyleSheet("background: white; border-radius: 15px;")
        self.charts_layout = QVBoxLayout()
        self.charts_layout.setContentsMargins(20, 20, 20, 20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        scroll_content = QWidget()
        scroll_content.setLayout(self.charts_layout)
        scroll.setWidget(scroll_content)

        charts_container_layout = QVBoxLayout()
        charts_container_layout.addWidget(scroll)
        charts_container_layout.setContentsMargins(0, 0, 0, 0)
        self.charts_widget.setLayout(charts_container_layout)

        # History Tab
        self.history_widget = QWidget()
        self.history_widget.setStyleSheet("background: white; border-radius: 15px;")
        self.history_layout = QVBoxLayout()
        self.history_layout.setContentsMargins(30, 30, 30, 30)
        self.history_layout.setSpacing(15)
        
        # Refresh button for history
        history_button_layout = QHBoxLayout()
        history_refresh_btn = ModernButton("🔄 Refresh History", "🔄", "#14b8a6")
        history_refresh_btn.clicked.connect(self.load_history)
        history_button_layout.addWidget(history_refresh_btn)
        history_button_layout.addStretch()
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setStyleSheet("""
            QTextEdit {
                background-color: #F0FDFA;
                border: 2px solid #99f6e4;
                border-radius: 10px;
                padding: 20px;
                color: #134E4A;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        
        self.history_layout.addLayout(history_button_layout)
        self.history_layout.addWidget(self.history_text)
        self.history_widget.setLayout(self.history_layout)

        # Add tabs
        self.tabs.addTab(self.summary_widget, "📊  Summary")
        self.tabs.addTab(self.table_widget, "📋  Data Table")
        self.tabs.addTab(self.charts_widget, "📈  Visualizations")
        self.tabs.addTab(self.history_widget, "📚  Upload History")
        
        # Connect tab change signal to load history
        self.tabs.currentChanged.connect(self.on_tab_changed)

        main_layout.addWidget(self.tabs, 1)

        central_widget.setLayout(main_layout)

    def update_status(self, message, status_type="info"):
        """Update status label with icon and color"""
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "loading": "⏳"
        }
        colors = {
            "info": "#0891b2",
            "success": "#14b8a6",
            "error": "#ef4444",
            "loading": "#f59e0b"
        }
        backgrounds = {
            "info": "#CFFAFE",
            "success": "#CCFBF1",
            "error": "#FEE2E2",
            "loading": "#FEF3C7"
        }

        icon = icons.get(status_type, "ℹ️")
        color = colors.get(status_type, "#0891b2")
        bg = backgrounds.get(status_type, "#CCFBF1")

        self.status_label.setText(f"{icon} {message}")
        self.status_label.setStyleSheet(f"""
            color: #134E4A;
            padding: 10px 15px;
            background-color: {bg};
            border-radius: 8px;
            border-left: 4px solid {color};
            font-weight: 500;
        """)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv)"
        )

        if file_path:
            try:
                self.update_status("Uploading file...", "loading")
                QApplication.processEvents()

                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(self.api_url, files=files)
                    response.raise_for_status()

                    self.current_data = response.json()
                    file_name = file_path.split('/')[-1].split('\\\\')[-1]
                    self.update_status(f"Successfully uploaded: {file_name}", "success")
                    self.update_display()

                    QMessageBox.information(
                        self,
                        "Success",
                        f"✅ File uploaded successfully!\n\n"
                        f"{self.current_data['summary']['total_count']} records processed."
                    )

            except requests.exceptions.ConnectionError:
                self.update_status("Connection failed - Check backend server", "error")
                QMessageBox.critical(
                    self,
                    "Connection Error",
                    "⚠️ Cannot connect to Django backend.\n\n"
                    "Make sure it's running at http://localhost:8000"
                )
            except Exception as e:
                self.update_status(f"Upload failed: {str(e)}", "error")
                QMessageBox.critical(self, "Error", f"❌ Error uploading file:\n\n{str(e)}")

    def update_display(self):
        if not self.current_data:
            return

        summary = self.current_data['summary']
        data = self.current_data['data']

        # Update cards
        self.update_card(self.card1, "Total Equipment", str(summary['total_count']))
        self.update_card(self.card2, "Avg Flowrate", f"{summary['avg_flowrate']:.2f}")
        self.update_card(self.card3, "Avg Pressure", f"{summary['avg_pressure']:.2f}")
        self.update_card(self.card4, "Avg Temperature", f"{summary['avg_temperature']:.2f}")

        # Update summary with teal-themed HTML
        summary_html = f"""
        <div style='padding: 30px;'>
            <h2 style='color: #134E4A; font-size: 24px; margin-bottom: 20px;
                       border-bottom: 3px solid #14b8a6; padding-bottom: 10px;'>
                📊 Statistical Summary
            </h2>

            <div style='background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
                        padding: 25px; border-radius: 12px; margin: 20px 0; color: white;'>
                <h3 style='font-size: 18px; margin-bottom: 15px;'>📦 Dataset Overview</h3>
                <p style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                    {summary['total_count']}
                </p>
                <p style='opacity: 0.95;'>Total Equipment Records</p>
            </div>

            <div style='display: grid; grid-template-columns: 1fr 1fr 1fr;
                        gap: 15px; margin-top: 20px;'>
                <div style='background: #CCFBF1; padding: 20px; border-radius: 10px;
                            border-left: 4px solid #14b8a6;'>
                    <p style='color: #0d9488; font-size: 13px; margin-bottom: 8px;
                              font-weight: 600;'>💧 AVERAGE FLOWRATE</p>
                    <p style='color: #134E4A; font-size: 24px; font-weight: bold;'>
                        {summary['avg_flowrate']:.2f}
                    </p>
                </div>
                <div style='background: #CFFAFE; padding: 20px; border-radius: 10px;
                            border-left: 4px solid #0891b2;'>
                    <p style='color: #0891b2; font-size: 13px; margin-bottom: 8px;
                              font-weight: 600;'>⚡ AVERAGE PRESSURE</p>
                    <p style='color: #134E4A; font-size: 24px; font-weight: bold;'>
                        {summary['avg_pressure']:.2f}
                    </p>
                </div>
                <div style='background: #E0F2FE; padding: 20px; border-radius: 10px;
                            border-left: 4px solid #06b6d4;'>
                    <p style='color: #06b6d4; font-size: 13px; margin-bottom: 8px;
                              font-weight: 600;'>🌡️ AVERAGE TEMPERATURE</p>
                    <p style='color: #134E4A; font-size: 24px; font-weight: bold;'>
                        {summary['avg_temperature']:.2f}
                    </p>
                </div>
            </div>

            <div style='background: #F0FDFA; padding: 20px; border-radius: 10px;
                        margin-top: 20px; border: 2px solid #99f6e4;'>
                <h3 style='color: #134E4A; font-size: 16px; margin-bottom: 15px;'>
                    📈 Equipment Type Distribution
                </h3>
                {''.join([
                    f"<div style='margin: 8px 0; padding: 10px; background: white;"
                    f" border-radius: 6px; border-left: 3px solid #14b8a6;'>"
                    f"<span style='color: #0d9488;'>{k}:</span> "
                    f"<strong style='color: #134E4A;'>{v} units</strong></div>"
                    for k, v in summary['equipment_types'].items()
                ])}
            </div>
        </div>
        """

        self.summary_label.setText(summary_html)
        self.summary_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Update table
        df = pd.DataFrame(data)
        self.table_widget.setRowCount(len(df))
        self.table_widget.setColumnCount(len(df.columns))
        self.table_widget.setHorizontalHeaderLabels(df.columns)

        for i, row in df.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                item.setFont(QFont("Segoe UI", 12))
                self.table_widget.setItem(i, j, item)

        # Auto-resize columns with minimum width for visibility
        self.table_widget.resizeColumnsToContents()
        for i in range(self.table_widget.columnCount()):
            width = self.table_widget.columnWidth(i)
            self.table_widget.setColumnWidth(i, max(width, 120))

        # Update charts
        self.update_charts(summary, df)

        # Enable PDF button
        self.pdf_btn.setEnabled(True)

    def update_card(self, card, title, value):
        """Update card value"""
        for child in card.findChildren(QLabel):
            # value label uses font size 24
            if child.font().pointSize() == 24:
                child.setText(value)
                break

    def update_charts(self, summary, df):
        # Clear previous charts
        for i in reversed(range(self.charts_layout.count())):
            widget = self.charts_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Teal color scheme for charts
        plt.style.use('seaborn-v0_8-whitegrid')

        # Bar chart
        fig1 = Figure(figsize=(12, 5), facecolor='white')
        ax1 = fig1.add_subplot(111)
        params = ['Flowrate', 'Pressure', 'Temperature']
        values = [
            summary['avg_flowrate'],
            summary['avg_pressure'],
            summary['avg_temperature']
        ]
        colors_bar = ['#14b8a6', '#0891b2', '#06b6d4']

        bars = ax1.bar(
            params,
            values,
            color=colors_bar,
            edgecolor='white',
            linewidth=2,
            width=0.6
        )
        ax1.set_title(
            'Average Parameters',
            fontsize=18,
            fontweight='bold',
            pad=20,
            color='#134E4A'
        )
        ax1.set_ylabel('Value', fontsize=13, color='#0d9488')
        ax1.tick_params(colors='#134E4A')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#99f6e4')
        ax1.spines['bottom'].set_color('#99f6e4')
        ax1.grid(axis='y', alpha=0.3, linestyle='--', color='#99f6e4')
        ax1.set_facecolor('#F0FDFA')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f'{height:.1f}',
                ha='center',
                va='bottom',
                fontweight='bold',
                fontsize=11,
                color='#134E4A'
            )

        fig1.tight_layout()
        canvas1 = FigureCanvas(fig1)
        self.charts_layout.addWidget(canvas1)

        # Pie chart
        fig2 = Figure(figsize=(12, 5), facecolor='white')
        ax2 = fig2.add_subplot(111)
        equipment_types = summary['equipment_types']
        colors_pie = ['#14b8a6', '#0891b2', '#06b6d4', '#2dd4bf', '#5eead4', '#99f6e4']

        wedges, texts, autotexts = ax2.pie(
            list(equipment_types.values()),
            labels=list(equipment_types.keys()),
            autopct='%1.1f%%',
            colors=colors_pie,
            startangle=90,
            textprops={
                'fontsize': 11,
                'color': '#134E4A',
                'fontweight': 'bold'
            }
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)

        ax2.set_title(
            'Equipment Type Distribution',
            fontsize=18,
            fontweight='bold',
            pad=20,
            color='#134E4A'
        )
        ax2.set_facecolor('#F0FDFA')
        fig2.patch.set_facecolor('#F0FDFA')
        fig2.tight_layout()

        canvas2 = FigureCanvas(fig2)
        self.charts_layout.addWidget(canvas2)

    def on_tab_changed(self, index):
        """Handle tab changes - load history when history tab is opened"""
        if index == 3:  # History tab
            self.load_history()

    def load_history(self):
        """Load upload history in the History tab"""
        try:
            response = requests.get('http://localhost:8000/api/datasets/')
            response.raise_for_status()
            datasets = response.json()[:10]

            if not datasets:
                self.history_text.setHtml("""
                    <div style='text-align: center; padding: 60px; color: #0d9488;'>
                        <h2 style='font-size: 24px; margin-bottom: 15px;'>📚 No Upload History</h2>
                        <p>Click "Upload CSV File" to add your first dataset</p>
                    </div>
                """)
                return

            history_html = """
            <div style='padding: 10px;'>
                <div style='background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
                            color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px;'>
                    <h1 style='margin: 0; font-size: 28px;'>📚 Upload History</h1>
                    <p style='margin: 5px 0 0 0; opacity: 0.95; font-size: 14px;'>
                        Showing {0} recent datasets
                    </p>
                </div>
            """.format(len(datasets))

            for idx, dataset in enumerate(datasets, 1):
                is_current = self.current_data and self.current_data.get('id') == dataset['id']
                current_badge = (
                    '<span style="background: #06b6d4; color: white; padding: 4px 12px; '
                    'border-radius: 8px; font-size: 12px; margin-left: 12px; font-weight: bold;">'
                    'CURRENT</span>' if is_current else ''
                )
                
                bg_color = "#CCFBF1" if is_current else "white"
                border_color = "#06b6d4" if is_current else "#14b8a6"

                history_html += f"""
                <div style='background: {bg_color}; padding: 25px; margin: 20px 0; 
                            border-radius: 12px; border-left: 5px solid {border_color};
                            box-shadow: 0 2px 8px rgba(20, 184, 166, 0.15);'>
                    <h3 style='color: #134E4A; margin: 0 0 15px 0; font-size: 18px; font-weight: 700;'>
                        <span style='background: #14b8a6; color: white; padding: 6px 14px;
                                     border-radius: 20px; font-size: 13px; margin-right: 12px;'>
                            #{idx}
                        </span>
                        {dataset['name']}
                        {current_badge}
                    </h3>
                    <p style='color: #0d9488; margin: 10px 0; font-size: 13px; font-weight: 500;'>
                        📅 {dataset['uploaded_at'][:19].replace('T', ' at ')}
                    </p>
                    <div style='display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 20px; margin-top: 15px;'>
                        <div style='background: white; padding: 15px; border-radius: 8px; 
                                    border-left: 3px solid #14b8a6;'>
                            <p style='color: #0d9488; font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>📦 Items</p>
                            <p style='color: #134E4A; font-size: 20px; font-weight: 700; margin: 0;'>
                                {dataset['total_count']}
                            </p>
                        </div>
                        <div style='background: white; padding: 15px; border-radius: 8px;
                                    border-left: 3px solid #0891b2;'>
                            <p style='color: #0d9488; font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>💧 Flowrate</p>
                            <p style='color: #134E4A; font-size: 20px; font-weight: 700; margin: 0;'>
                                {dataset['avg_flowrate']:.2f}
                            </p>
                        </div>
                        <div style='background: white; padding: 15px; border-radius: 8px;
                                    border-left: 3px solid #06b6d4;'>
                            <p style='color: #0d9488; font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>⚡ Pressure</p>
                            <p style='color: #134E4A; font-size: 20px; font-weight: 700; margin: 0;'>
                                {dataset['avg_pressure']:.2f}
                            </p>
                        </div>
                        <div style='background: white; padding: 15px; border-radius: 8px;
                                    border-left: 3px solid #2dd4bf;'>
                            <p style='color: #0d9488; font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>🌡️ Temp</p>
                            <p style='color: #134E4A; font-size: 20px; font-weight: 700; margin: 0;'>
                                {dataset['avg_temperature']:.2f}
                            </p>
                        </div>
                    </div>
                </div>
                """

            history_html += "</div>"
            
            self.history_text.setHtml(history_html)
            self.update_status("Upload history loaded", "success")

        except Exception as e:
            self.history_text.setHtml(f"""
                <div style='text-align: center; padding: 60px; color: #ef4444;'>
                    <h2 style='font-size: 24px; margin-bottom: 15px;'>❌ Error Loading History</h2>
                    <p style='font-size: 14px;'>{str(e)}</p>
                    <p style='font-size: 12px; color: #0d9488; margin-top: 20px;'>
                        Make sure the backend server is running at http://localhost:8000
                    </p>
                </div>
            """)
            self.update_status("Failed to load history", "error")

    def show_history(self):
        """Show upload history in the History tab"""
        try:
            response = requests.get('http://localhost:8000/api/datasets/')
            response.raise_for_status()
            datasets = response.json()[:10]

            if not datasets:
                self.history_text.setText("""
                    <div style='text-align: center; padding: 60px; color: #0d9488;'>
                        <h2 style='font-size: 24px; margin-bottom: 15px;'>📚 No Upload History</h2>
                        <p>Click "Upload CSV File" to add your first dataset</p>
                    </div>
                """)
                self.tabs.setCurrentIndex(3)
                return

            history_html = """
            <div style='padding: 10px;'>
                <div style='background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
                            color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px;'>
                    <h1 style='margin: 0; font-size: 28px;'>📚 Upload History</h1>
                    <p style='margin: 5px 0 0 0; opacity: 0.95; font-size: 14px;'>
                        Showing {0} recent datasets
                    </p>
                </div>
            """.format(len(datasets))

            for idx, dataset in enumerate(datasets, 1):
                is_current = self.current_data and self.current_data.get('id') == dataset['id']
                current_badge = (
                    '<span style="background: #06b6d4; color: white; padding: 4px 12px; '
                    'border-radius: 8px; font-size: 12px; margin-left: 12px; font-weight: bold;">'
                    'CURRENT</span>' if is_current else ''
                )
                
                bg_color = "#CCFBF1" if is_current else "white"
                border_color = "#06b6d4" if is_current else "#14b8a6"

                history_html += f"""
                <div style='background: {bg_color}; padding: 25px; margin: 20px 0; 
                            border-radius: 12px; border-left: 5px solid {border_color};
                            box-shadow: 0 2px 8px rgba(20, 184, 166, 0.15);'>
                    <h3 style='color: #134E4A; margin: 0 0 15px 0; font-size: 18px; font-weight: 700;'>
                        <span style='background: #14b8a6; color: white; padding: 6px 14px;
                                     border-radius: 20px; font-size: 13px; margin-right: 12px;'>
                            #{idx}
                        </span>
                        {dataset['name']}
                        {current_badge}
                    </h3>
                    <p style='color: #0d9488; margin: 10px 0; font-size: 13px; font-weight: 500;'>
                        📅 {dataset['uploaded_at'][:19].replace('T', ' at ')}
                    </p>
                    <div style='display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 20px; margin-top: 15px;'>
                        <div style='background: white; padding: 15px; border-radius: 8px; 
                                    border-left: 3px solid #14b8a6;'>
                            <p style='color: #0d9488; font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>📦 Items</p>
                            <p style='color: #134E4A; font-size: 20px; font-weight: 700; margin: 0;'>
                                {dataset['total_count']}
                            </p>
                        </div>
                        <div style='background: white; padding: 15px; border-radius: 8px;
                                    border-left: 3px solid #0891b2;'>
                            <p style='color: #0d9488; font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>💧 Flowrate</p>
                            <p style='color: #134E4A; font-size: 20px; font-weight: 700; margin: 0;'>
                                {dataset['avg_flowrate']:.2f}
                            </p>
                        </div>
                        <div style='background: white; padding: 15px; border-radius: 8px;
                                    border-left: 3px solid #06b6d4;'>
                            <p style='color: #0d9488; font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>⚡ Pressure</p>
                            <p style='color: #134E4A; font-size: 20px; font-weight: 700; margin: 0;'>
                                {dataset['avg_pressure']:.2f}
                            </p>
                        </div>
                        <div style='background: white; padding: 15px; border-radius: 8px;
                                    border-left: 3px solid #2dd4bf;'>
                            <p style='color: #0d9488; font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>🌡️ Temp</p>
                            <p style='color: #134E4A; font-size: 20px; font-weight: 700; margin: 0;'>
                                {dataset['avg_temperature']:.2f}
                            </p>
                        </div>
                    </div>
                </div>
                """

            history_html += "</div>"
            
            self.history_text.setHtml(history_html)
            self.tabs.setCurrentIndex(3)
            self.update_status("Upload history loaded", "success")

        except Exception as e:
            self.history_text.setText(f"""
                <div style='text-align: center; padding: 60px; color: #ef4444;'>
                    <h2 style='font-size: 24px; margin-bottom: 15px;'>❌ Error Loading History</h2>
                    <p>{str(e)}</p>
                </div>
            """)
            self.update_status("Failed to load history", "error")

    def show_history(self):
        """Show upload history - switch to history tab and load data"""
        self.tabs.setCurrentIndex(3)
        self.load_history()

    def download_pdf(self):
        if not self.current_data:
            return

        username, ok1 = QInputDialog.getText(
            self, "Authentication", "Username:", text="admin"
        )
        if not ok1:
            return

        password, ok2 = QInputDialog.getText(
            self,
            "Authentication",
            "Password:",
            echo=QLineEdit.Password
        )
        if not ok2:
            return

        try:
            dataset_id = self.current_data['id']
            url = f"http://localhost:8000/api/datasets/{dataset_id}/generate_report/"

            from requests.auth import HTTPBasicAuth
            response = requests.get(url, auth=HTTPBasicAuth(username, password))
            response.raise_for_status()

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF Report",
                "equipment_report.pdf",
                "PDF Files (*.pdf)"
            )

            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                self.update_status("PDF saved successfully!", "success")
                QMessageBox.information(
                    self,
                    "Success",
                    f"✅ PDF report saved to:\n\n{file_path}"
                )

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                QMessageBox.critical(
                    self,
                    "Authentication Failed",
                    "❌ Invalid username or password"
                )
                self.update_status("Authentication failed", "error")
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"❌ Error generating PDF:\n\n{str(e)}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Error:\n\n{str(e)}")

    def refresh_data(self):
        """Refresh the display"""
        if self.current_data:
            self.update_display()
            self.update_status("Data refreshed successfully", "success")
        else:
            self.update_status("No data to refresh", "info")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = EquipmentVisualizerApp()
    window.show()
    sys.exit(app.exec_())

